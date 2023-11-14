"""Client."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Callable
from copy import deepcopy
from datetime import datetime
import functools
import logging
from operator import itemgetter
import pprint
from types import TracebackType
from typing import Any, cast
import uuid

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType, client_exceptions

from .const import (
    LOG_LEVEL_MAP,
    MAX_SERVER_SCHEMA_VERSION,
    MIN_SERVER_SCHEMA_VERSION,
    PACKAGE_NAME,
    LogLevel,
    __version__,
)
from .event import Event
from .exceptions import (
    CannotConnect,
    ConnectionClosed,
    ConnectionFailed,
    FailedCommand,
    FailedZWaveCommand,
    InvalidMessage,
    InvalidServerVersion,
    InvalidState,
    NotConnected,
)
from .model.driver import Driver
from .model.log_message import LogMessage
from .model.version import VersionInfo, VersionInfoDataType

try:
    import orjson as json
except ImportError:
    import json

SIZE_PARSE_JSON_EXECUTOR = 8192

# Message IDs
INITIALIZE_MESSAGE_ID = "initialize"
GET_INITIAL_LOG_CONFIG_MESSAGE_ID = "get-initial-log-config"
START_LISTENING_MESSAGE_ID = "start-listening"

LISTEN_MESSAGE_IDS = (
    GET_INITIAL_LOG_CONFIG_MESSAGE_ID,
    INITIALIZE_MESSAGE_ID,
    START_LISTENING_MESSAGE_ID,
)

LOGGER = logging.getLogger(__package__)
SERVER_LOGGER = logging.getLogger(f"{__package__}.server")


class Client:
    """Class to manage the IoT connection."""

    def __init__(
        self,
        ws_server_url: str,
        aiohttp_session: ClientSession,
        schema_version: int = MAX_SERVER_SCHEMA_VERSION,
        additional_user_agent_components: dict[str, str] | None = None,
        record_messages: bool = False,
    ):
        """Initialize the Client class."""
        self.ws_server_url = ws_server_url
        self.aiohttp_session = aiohttp_session
        self.driver: Driver | None = None
        # The WebSocket client
        self._client: ClientWebSocketResponse | None = None
        # Version of the connected server
        self.version: VersionInfo | None = None
        self.schema_version: int = schema_version
        self.additional_user_agent_components = {
            PACKAGE_NAME: __version__,
            **(additional_user_agent_components or {}),
        }
        self._loop = asyncio.get_running_loop()
        self._result_futures: dict[str, asyncio.Future] = {}
        self._shutdown_complete_event: asyncio.Event | None = None

        self._server_logger_unsubs: list[Callable[[], None]] = []
        self._server_logging_enabled: bool = False

        self._record_messages = record_messages
        self._recorded_commands: defaultdict[str, dict] = defaultdict(dict)
        self._recorded_events: list[dict] = []

    def __repr__(self) -> str:
        """Return the representation."""
        prefix = "" if self.connected else "not "
        return (
            f"{type(self).__name__}(ws_server_url={self.ws_server_url!r}, "
            f"{prefix}connected)"
        )

    @property
    def connected(self) -> bool:
        """Return if we're currently connected."""
        return self._client is not None and not self._client.closed

    @property
    def recording_messages(self) -> bool:
        """Return True if messages are being recorded."""
        return self._record_messages

    async def async_send_command(
        self, message: dict[str, Any], require_schema: int | None = None
    ) -> dict:
        """Send a command and get a response."""
        if require_schema is not None and require_schema > self.schema_version:
            assert self.version
            raise InvalidServerVersion(
                self.version,
                require_schema,
                "Command not available due to incompatible server version. Update "
                "the Z-Wave JS Server to a version that supports at least api schema "
                f"{require_schema}.",
            )
        future: asyncio.Future[dict] = self._loop.create_future()
        message_id = message["messageId"] = uuid.uuid4().hex
        self._result_futures[message_id] = future
        await self._send_json_message(message)
        try:
            return await future
        finally:
            self._result_futures.pop(message_id, None)

    async def async_send_command_no_wait(
        self, message: dict[str, Any], require_schema: int | None = None
    ) -> None:
        """Send a command without waiting for the response."""
        if require_schema is not None and require_schema > self.schema_version:
            assert self.version
            raise InvalidServerVersion(
                self.version,
                require_schema,
                "Command not available due to incompatible server version. Update "
                "the Z-Wave JS Server to a version that supports at least api schema "
                f"{require_schema}.",
            )
        message["messageId"] = uuid.uuid4().hex
        await self._send_json_message(message)

    async def connect(self) -> None:
        """Connect to the websocket server."""
        if self.driver is not None:
            raise InvalidState("Re-connected with existing driver")

        LOGGER.debug("Trying to connect")
        try:
            self._client = await self.aiohttp_session.ws_connect(
                self.ws_server_url,
                heartbeat=55,
                compress=15,
                max_msg_size=0,
            )
        except (
            client_exceptions.WSServerHandshakeError,
            client_exceptions.ClientError,
        ) as err:
            raise CannotConnect(err) from err

        self.version = version = VersionInfo.from_message(
            cast(VersionInfoDataType, await self._receive_json_or_raise())
        )

        # basic check for server schema version compatibility
        if (
            version.min_schema_version > MAX_SERVER_SCHEMA_VERSION
            or version.max_schema_version < MIN_SERVER_SCHEMA_VERSION
        ):
            await self._client.close()
            assert version
            raise InvalidServerVersion(
                version,
                MIN_SERVER_SCHEMA_VERSION,
                f"Z-Wave JS Server version ({version.server_version}) is "
                "incompatible. Update the Z-Wave JS Server to a version that supports "
                f"at least api schema {MIN_SERVER_SCHEMA_VERSION}",
            )
        # store the (highest possible) schema version we're going to use/request
        # this is a bit future proof as we might decide to use a pinned version at some
        # point for now we just negotiate the highest available schema version and
        # guard incompatibility with the MIN_SERVER_SCHEMA_VERSION
        if version.max_schema_version < MAX_SERVER_SCHEMA_VERSION:
            self.schema_version = version.max_schema_version

        LOGGER.info(
            "Connected to Home %s (Server %s, Driver %s, Using Schema %s)",
            version.home_id,
            version.server_version,
            version.driver_version,
            self.schema_version,
        )

    async def initialize(self) -> None:
        """Initialize connection to server by setting schema version and user agent."""
        assert self._client

        # set preferred schema version on the server
        # note: we already check for (in)compatible schemas in the connect call
        await self._send_json_message(
            {
                "command": "initialize",
                "messageId": INITIALIZE_MESSAGE_ID,
                "schemaVersion": self.schema_version,
                "additionalUserAgentComponents": self.additional_user_agent_components,
            }
        )
        set_api_msg = await self._receive_json_or_raise()

        if not set_api_msg["success"]:
            # this should not happen, but just in case
            await self._client.close()
            raise FailedCommand(
                set_api_msg["messageId"],
                set_api_msg["errorCode"],
                set_api_msg["message"],
            )

    async def listen(self, driver_ready: asyncio.Event) -> None:
        """Start listening to the websocket."""
        if not self.connected:
            raise InvalidState("Not connected when start listening")

        assert self._client

        try:
            await self.initialize()

            await self._send_json_message(
                {
                    "command": "driver.get_log_config",
                    "messageId": GET_INITIAL_LOG_CONFIG_MESSAGE_ID,
                }
            )

            log_msg = await self._receive_json_or_raise()

            # this should not happen, but just in case
            if not log_msg["success"]:
                await self._client.close()
                raise FailedCommand(
                    log_msg["messageId"], log_msg["errorCode"], log_msg["message"]
                )

            # send start_listening command to the server
            # we will receive a full state dump and from now on get events
            await self._send_json_message(
                {"command": "start_listening", "messageId": START_LISTENING_MESSAGE_ID}
            )

            state_msg = await self._receive_json_or_raise()

            if not state_msg["success"]:
                await self._client.close()
                raise FailedCommand(
                    state_msg["messageId"], state_msg["errorCode"], state_msg["message"]
                )

            self.driver = cast(
                Driver,
                await self._loop.run_in_executor(
                    None,
                    Driver,
                    self,
                    state_msg["result"]["state"],
                    log_msg["result"]["config"],
                ),
            )

            driver_ready.set()

            LOGGER.info(
                "Z-Wave JS initialized. %s nodes", len(self.driver.controller.nodes)
            )

            await self.receive_until_closed()
        except ConnectionClosed:
            pass

        finally:
            LOGGER.debug("Listen completed. Cleaning up")

            for future in self._result_futures.values():
                future.cancel()
            self._result_futures.clear()

            if not self._client.closed:
                await self._client.close()

            if self._shutdown_complete_event:
                self._shutdown_complete_event.set()

    async def disconnect(self) -> None:
        """Disconnect the client."""
        LOGGER.debug("Closing client connection")

        if not self.connected:
            return

        assert self._client

        # 'listen' was never called
        if self.driver is None:
            await self._client.close()
            return

        self._shutdown_complete_event = asyncio.Event()
        await self._client.close()
        await self._shutdown_complete_event.wait()

        self._shutdown_complete_event = None
        self.driver = None

    async def async_start_listening_logs(self) -> None:
        """Send command to start listening to log events."""
        await self.async_send_command(
            {"command": "start_listening_logs"}, require_schema=31
        )

    async def async_stop_listening_logs(self) -> None:
        """Send command to stop listening to log events."""
        await self.async_send_command(
            {"command": "stop_listening_logs"}, require_schema=31
        )

    def begin_recording_messages(self) -> None:
        """Begin recording messages for replay later."""
        if self._record_messages:
            raise InvalidState("Already recording messages")

        self._record_messages = True

    def end_recording_messages(self) -> list[dict]:
        """End recording messages and return messages that were recorded."""
        if not self._record_messages:
            raise InvalidState("Not recording messages")

        self._record_messages = False

        data = sorted(
            (*self._recorded_commands.values(), *self._recorded_events),
            key=itemgetter("ts"),
        )
        self._recorded_commands.clear()
        self._recorded_events.clear()

        return list(data)

    @property
    def server_logging_enabled(self) -> bool:
        """Return whether server logging is currently enabled."""
        return self._server_logging_enabled

    async def enable_server_logging(self) -> None:
        """
        Enable logging from the server.

        Embeds server logs in the library's logs.
        """
        if not self.connected or not self.driver:
            raise InvalidState(
                "Can't enable server logging when not connected to server"
            )
        if (log_level := self.driver.log_config.level) and (
            level := LOG_LEVEL_MAP[log_level]
        ) < LOGGER.level:
            LOGGER.warning(
                (
                    "Server logging is currently more verbose than library logging, "
                    "setting library log level to %s to match."
                ),
                logging.getLevelName(level),
            )
            LOGGER.setLevel(level)

        if self._server_logging_enabled:
            return

        self._server_logging_enabled = True

        def handle_server_logs(event: dict) -> None:
            """Handle driver `logging` event."""
            log_msg: LogMessage = event["log_message"]
            log_level = LogLevel(log_msg.level)
            SERVER_LOGGER.log(
                LOG_LEVEL_MAP[log_level],
                "%s:\n%s",
                log_msg.timestamp,
                "\n".join(log_msg.formatted_message),
            )

        def handle_log_config_updates(event: dict) -> None:
            """Handle driver `log config updated` events."""
            if (log_level := event["config"]["level"].lower()) and (
                level := LOG_LEVEL_MAP[log_level]
            ) < LOGGER.level:
                LOGGER.warning(
                    (
                        "Server logging is currently more verbose than library "
                        "logging, setting library log level to %s to match."
                    ),
                    logging.getLevelName(level),
                )
            LOGGER.setLevel(level)

        self._server_logger_unsubs = [
            self.driver.on("logging", handle_server_logs),
            self.driver.on("log config updated", handle_log_config_updates),
        ]

        await self.async_start_listening_logs()

    async def disable_server_logging(self) -> None:
        """Disable logging from the server."""
        if not self.connected or not self.driver:
            raise InvalidState(
                "Can't disable server logging when not connected to server"
            )
        if not self._server_logging_enabled or not self._server_logger_unsubs:
            LOGGER.info("Server logging is already disabled")
            return

        for unsub in self._server_logger_unsubs:
            unsub()
        self._server_logger_unsubs.clear()
        self._server_logging_enabled = False

    async def receive_until_closed(self) -> None:
        """Receive messages until client is closed."""
        assert self._client

        while not self._client.closed:
            data = await self._receive_json_or_raise()

            self._handle_incoming_message(data)

    async def _receive_json_or_raise(self) -> dict:
        """Receive json or raise."""
        assert self._client
        msg = await self._client.receive()

        if msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.CLOSING):
            raise ConnectionClosed("Connection was closed.")

        if msg.type == WSMsgType.ERROR:
            raise ConnectionFailed()

        if msg.type != WSMsgType.TEXT:
            raise InvalidMessage(f"Received non-Text message: {msg.type}")

        try:
            if len(msg.data) > SIZE_PARSE_JSON_EXECUTOR:
                data: dict = await self._loop.run_in_executor(
                    None, functools.partial(msg.json, loads=json.loads)
                )
            else:
                data = msg.json(loads=json.loads)
        except ValueError as err:
            raise InvalidMessage("Received invalid JSON.") from err

        if LOGGER.isEnabledFor(logging.DEBUG) and not (
            self.server_logging_enabled
            and data.get("type") == "event"
            and data.get("event", {}).get("event") == "logging"
        ):
            LOGGER.debug("Received message:\n%s\n", pprint.pformat(msg))

        return data

    def _handle_incoming_message(self, msg: dict) -> None:
        """Handle incoming message.

        Run all async tasks in a wrapper to log appropriately.
        """
        if msg["type"] == "result":
            future = self._result_futures.get(msg["messageId"])

            if future is None or future.cancelled():
                # no listener for this result or the future was canceled
                return

            if self._record_messages and msg["messageId"] not in LISTEN_MESSAGE_IDS:
                self._recorded_commands[msg["messageId"]].update(
                    {
                        "result_ts": datetime.utcnow().isoformat(),
                        "result_msg": deepcopy(msg),
                    }
                )

            if msg["success"]:
                future.set_result(msg["result"])
                return

            if msg["errorCode"] != "zwave_error":
                err = FailedCommand(msg["messageId"], msg["errorCode"], msg["message"])
            else:
                err = FailedZWaveCommand(
                    msg["messageId"], msg["zwaveErrorCode"], msg["zwaveErrorMessage"]
                )

            future.set_exception(err)
            return

        if msg["type"] != "event":
            # Can't handle
            LOGGER.debug(
                "Received message with unknown type '%s': %s",
                msg["type"],
                msg,
            )
            return

        if self._record_messages and not (
            self.server_logging_enabled and msg["event"]["event"] == "logging"
        ):
            self._recorded_events.append(
                {
                    "record_type": "event",
                    "ts": datetime.utcnow().isoformat(),
                    "type": msg["event"]["event"],
                    "event_msg": deepcopy(msg),
                }
            )

        event = Event(type=msg["event"]["event"], data=msg["event"])
        self.driver.receive_event(event)  # type: ignore

    async def _send_json_message(self, message: dict[str, Any]) -> None:
        """Send a message.

        Raises NotConnected if client not connected.
        """
        if not self.connected:
            raise NotConnected

        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug("Publishing message:\n%s\n", pprint.pformat(message))

        assert self._client
        assert "messageId" in message

        if self._record_messages and message["messageId"] not in LISTEN_MESSAGE_IDS:
            # We don't need to deepcopy command_msg because it is always released by
            # the caller after the command is sent.
            self._recorded_commands[message["messageId"]].update(
                {
                    "record_type": "command",
                    "ts": datetime.utcnow().isoformat(),
                    "command": message["command"],
                    "command_msg": message,
                }
            )

        await self._client.send_json(message, dumps=json.dumps)

    async def __aenter__(self) -> Client:
        """Connect to the websocket."""
        await self.connect()
        return self

    async def __aexit__(
        self, exc_type: Exception, exc_value: str, traceback: TracebackType
    ) -> None:
        """Disconnect from the websocket."""
        await self.disconnect()
