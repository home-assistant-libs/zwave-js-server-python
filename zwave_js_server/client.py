"""Client."""
import asyncio
import logging
import pprint
import uuid
from types import TracebackType
from typing import Any, Dict, Optional, cast

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType, client_exceptions

from .const import MAX_SERVER_SCHEMA_VERSION, MIN_SERVER_SCHEMA_VERSION
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
from .model.version import VersionInfo

SIZE_PARSE_JSON_EXECUTOR = 8192


class Client:
    """Class to manage the IoT connection."""

    def __init__(
        self,
        ws_server_url: str,
        aiohttp_session: ClientSession,
        schema_version: int = MAX_SERVER_SCHEMA_VERSION,
    ):
        """Initialize the Client class."""
        self.ws_server_url = ws_server_url
        self.aiohttp_session = aiohttp_session
        self.driver: Optional[Driver] = None
        # The WebSocket client
        self._client: Optional[ClientWebSocketResponse] = None
        # Version of the connected server
        self.version: Optional[VersionInfo] = None
        self.schema_version: int = schema_version
        self._logger = logging.getLogger(__package__)
        self._loop = asyncio.get_running_loop()
        self._result_futures: Dict[str, asyncio.Future] = {}
        self._shutdown_complete_event: Optional[asyncio.Event] = None

    def __repr__(self) -> str:
        """Return the representation."""
        prefix = "" if self.connected else "not "
        return f"{type(self).__name__}(ws_server_url={self.ws_server_url!r}, {prefix}connected)"

    @property
    def connected(self) -> bool:
        """Return if we're currently connected."""
        return self._client is not None and not self._client.closed

    async def async_send_command(
        self,
        message: Dict[str, Any],
        require_schema: Optional[int] = None,
    ) -> dict:
        """Send a command and get a response."""
        if require_schema is not None and require_schema > self.schema_version:
            raise InvalidServerVersion(
                "Command not available due to incompatible server version. Update the Z-Wave "
                f"JS Server to a version that supports at least api schema {require_schema}."
            )
        future: "asyncio.Future[dict]" = self._loop.create_future()
        message_id = message["messageId"] = uuid.uuid4().hex
        self._result_futures[message_id] = future
        await self._send_json_message(message)
        try:
            return await future
        finally:
            self._result_futures.pop(message_id)

    async def async_send_command_no_wait(
        self, message: Dict[str, Any], require_schema: Optional[int] = None
    ) -> None:
        """Send a command without waiting for the response."""
        if require_schema is not None and require_schema > self.schema_version:
            raise InvalidServerVersion(
                "Command not available due to incompatible server version. Update the Z-Wave "
                f"JS Server to a version that supports at least api schema {require_schema}."
            )
        message["messageId"] = uuid.uuid4().hex
        await self._send_json_message(message)

    async def connect(self) -> None:
        """Connect to the websocket server."""
        if self.driver is not None:
            raise InvalidState("Re-connected with existing driver")

        self._logger.debug("Trying to connect")
        try:
            self._client = await self.aiohttp_session.ws_connect(
                self.ws_server_url,
                heartbeat=55,
            )
        except (
            client_exceptions.WSServerHandshakeError,
            client_exceptions.ClientError,
        ) as err:
            raise CannotConnect(err) from err

        self.version = version = VersionInfo.from_message(
            await self._receive_json_or_raise()
        )

        # basic check for server schema version compatability
        if (
            self.version.min_schema_version > MIN_SERVER_SCHEMA_VERSION
            or self.version.max_schema_version < MIN_SERVER_SCHEMA_VERSION
        ):
            await self._client.close()
            raise InvalidServerVersion(
                f"Z-Wave JS Server version is incompatible: {self.version.server_version} "
                "a version is required that supports at least "
                f"api schema {MIN_SERVER_SCHEMA_VERSION}"
            )
        # store the (highest possible) schema version we're going to use/request
        # this is a bit future proof as we might decide to use a pinned version at some point
        # for now we just negotiate the highest available schema version and
        # guard incompatibility with the MIN_SERVER_SCHEMA_VERSION
        if self.version.max_schema_version < MAX_SERVER_SCHEMA_VERSION:
            self.schema_version = self.version.max_schema_version

        self._logger.info(
            "Connected to Home %s (Server %s, Driver %s, Using Schema %s)",
            version.home_id,
            version.server_version,
            version.driver_version,
            self.schema_version,
        )

    async def set_api_schema(self) -> None:
        """Set API schema version on server."""
        assert self._client

        # set preferred schema version on the server
        # note: we already check for (in)compatible schemas in the connect call
        await self._send_json_message(
            {
                "command": "set_api_schema",
                "messageId": "api-schema-id",
                "schemaVersion": self.schema_version,
            }
        )
        set_api_msg = await self._receive_json_or_raise()

        if not set_api_msg["success"]:
            # this should not happen, but just in case
            await self._client.close()
            raise FailedCommand(set_api_msg["messageId"], set_api_msg["errorCode"])

    async def listen(self, driver_ready: asyncio.Event) -> None:
        """Start listening to the websocket."""
        if not self.connected:
            raise InvalidState("Not connected when start listening")

        assert self._client

        try:
            await self.set_api_schema()

            await self._send_json_message(
                {
                    "command": "driver.get_log_config",
                    "messageId": "get-initial-log-config",
                }
            )

            log_msg = await self._receive_json_or_raise()

            # this should not happen, but just in case
            if not log_msg["success"]:
                await self._client.close()
                raise FailedCommand(log_msg["messageId"], log_msg["errorCode"])

            # send start_listening command to the server
            # we will receive a full state dump and from now on get events
            await self._send_json_message(
                {"command": "start_listening", "messageId": "listen-id"}
            )

            state_msg = await self._receive_json_or_raise()

            if not state_msg["success"]:
                await self._client.close()
                raise FailedCommand(state_msg["messageId"], state_msg["errorCode"])

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

            self._logger.info(
                "Z-Wave JS initialized. %s nodes", len(self.driver.controller.nodes)
            )

            while not self._client.closed:
                data = await self._receive_json_or_raise()

                self._handle_incoming_message(data)
        except ConnectionClosed:
            pass

        finally:
            self._logger.debug("Listen completed. Cleaning up")

            for future in self._result_futures.values():
                future.cancel()

            if not self._client.closed:
                await self._client.close()

            if self._shutdown_complete_event:
                self._shutdown_complete_event.set()

    async def disconnect(self) -> None:
        """Disconnect the client."""
        self._logger.debug("Closing client connection")

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
                data: dict = await self._loop.run_in_executor(None, msg.json)
            else:
                data = msg.json()
        except ValueError as err:
            raise InvalidMessage("Received invalid JSON.") from err

        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("Received message:\n%s\n", pprint.pformat(msg))

        return data

    def _handle_incoming_message(self, msg: dict) -> None:
        """Handle incoming message.

        Run all async tasks in a wrapper to log appropriately.
        """
        if msg["type"] == "result":
            future = self._result_futures.get(msg["messageId"])

            if future is None:
                # no listener for this result
                return

            if msg["success"]:
                future.set_result(msg["result"])
                return

            if msg["errorCode"] != "zwave_error":
                err = FailedCommand(msg["messageId"], msg["errorCode"])
            else:
                err = FailedZWaveCommand(
                    msg["messageId"], msg["zwaveErrorCode"], msg["zwaveErrorMessage"]
                )

            future.set_exception(err)
            return

        if msg["type"] != "event":
            # Can't handle
            self._logger.debug(
                "Received message with unknown type '%s': %s",
                msg["type"],
                msg,
            )
            return

        event = Event(type=msg["event"]["event"], data=msg["event"])
        self.driver.receive_event(event)  # type: ignore

    async def _send_json_message(self, message: Dict[str, Any]) -> None:
        """Send a message.

        Raises NotConnected if client not connected.
        """
        if not self.connected:
            raise NotConnected

        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("Publishing message:\n%s\n", pprint.pformat(message))

        assert self._client
        assert "messageId" in message

        await self._client.send_json(message)

    async def __aenter__(self) -> "Client":
        """Connect to the websocket."""
        await self.connect()
        return self

    async def __aexit__(
        self, exc_type: Exception, exc_value: str, traceback: TracebackType
    ) -> None:
        """Disconnect from the websocket."""
        await self.disconnect()
