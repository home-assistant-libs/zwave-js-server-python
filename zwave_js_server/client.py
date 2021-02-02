"""Client."""
import asyncio
import logging
import pprint
import uuid
from types import TracebackType
from typing import Any, Dict, Optional, cast

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType, client_exceptions
from packaging.version import parse as parse_version

from .const import MIN_SERVER_VERSION
from .event import Event
from .exceptions import (
    CannotConnect,
    ConnectionFailed,
    FailedCommand,
    InvalidMessage,
    InvalidServerVersion,
    InvalidState,
    NotConnected,
)
from .model.driver import Driver
from .model.version import VersionInfo

STATE_CONNECTED = "connected"
STATE_DISCONNECTED = "disconnected"

SIZE_PARSE_JSON_EXECUTOR = 8192


class Client:
    """Class to manage the IoT connection."""

    def __init__(self, ws_server_url: str, aiohttp_session: ClientSession):
        """Initialize the Client class."""
        self.ws_server_url = ws_server_url
        self.aiohttp_session = aiohttp_session
        self.driver: Optional[Driver] = None
        # The WebSocket client
        self._client: Optional[ClientWebSocketResponse] = None
        # Current state of the connection
        self.state = STATE_DISCONNECTED
        # Version of the connected server
        self.version: Optional[VersionInfo] = None
        self._logger = logging.getLogger(__package__)
        self._loop = asyncio.get_running_loop()
        self._result_futures: Dict[str, asyncio.Future] = {}
        self._shutdown_complete_event: Optional[asyncio.Event] = None

    def __repr__(self) -> str:
        """Return the representation."""
        return (
            f"{type(self).__name__}(ws_server_url={self.ws_server_url!r}, {self.state})"
        )

    @property
    def connected(self) -> bool:
        """Return if we're currently connected."""
        return self.state == STATE_CONNECTED

    async def async_send_command(self, message: Dict[str, Any]) -> dict:
        """Send a command and get a response."""
        future: "asyncio.Future[dict]" = self._loop.create_future()
        message_id = message["messageId"] = uuid.uuid4().hex
        self._result_futures[message_id] = future
        await self._send_json_message(message)
        try:
            return await future
        finally:
            self._result_futures.pop(message_id)

    async def connect(self) -> None:
        """Connect to the websocket server."""
        if self.driver is not None:
            raise InvalidState("Re-connected with existing driver")

        client = None
        self._logger.debug("Trying to connect")
        try:
            self._client = client = await self.aiohttp_session.ws_connect(
                self.ws_server_url,
                heartbeat=55,
            )

            self.version = version = VersionInfo.from_message(
                await client.receive_json()
            )
        except (
            client_exceptions.WSServerHandshakeError,
            client_exceptions.ClientError,
        ) as err:
            raise CannotConnect(err) from err

        # basic check for server version compatability
        self._check_server_version(self.version.server_version)

        self._logger.info(
            "Connected to Home %s (Server %s, Driver %s)",
            version.home_id,
            version.server_version,
            version.driver_version,
        )
        self.state = STATE_CONNECTED

    async def listen(self, driver_ready: asyncio.Event) -> None:
        """Start listening to the websocket."""
        if self.state != STATE_CONNECTED:
            raise InvalidState("Not connected when start listening")

        start_listen_task = asyncio.create_task(self._start_listen(driver_ready))

        assert self._client

        try:
            while not self._client.closed:
                msg = await self._client.receive()

                if msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.CLOSING):
                    break

                if msg.type == WSMsgType.ERROR:
                    await self._client.close()
                    raise ConnectionFailed()

                if msg.type != WSMsgType.TEXT:
                    raise InvalidMessage(f"Received non-Text message: {msg.type}")

                try:
                    if len(msg.data) > SIZE_PARSE_JSON_EXECUTOR:
                        msg: dict = await self._loop.run_in_executor(None, msg.json)
                    else:
                        msg = msg.json()
                except ValueError as err:
                    raise InvalidMessage("Received invalid JSON.") from err

                if self._logger.isEnabledFor(logging.DEBUG):
                    self._logger.debug("Received message:\n%s\n", pprint.pformat(msg))

                self._handle_incoming_message(msg)

        finally:
            self._logger.debug("Listen completed. Cleaning up")

            for future in self._result_futures.values():
                future.cancel()

            start_listen_task.cancel()
            try:
                await start_listen_task
            except asyncio.CancelledError:
                pass

            if not self._client.closed:
                await self._client.close()

            self.state = STATE_DISCONNECTED

            if self._shutdown_complete_event:
                self._shutdown_complete_event.set()

    async def disconnect(self) -> None:
        """Disconnect the client."""
        self._logger.debug("Closing client connection")

        if self._client is None or self._client.closed:
            return

        self._shutdown_complete_event = asyncio.Event()
        await self._client.close()
        await self._shutdown_complete_event.wait()

    async def _start_listen(self, driver_ready: asyncio.Event) -> None:
        """Send start_listening command to initialize the driver."""
        result = await self.async_send_command({"command": "start_listening"})

        self.driver = cast(
            Driver,
            await self._loop.run_in_executor(None, Driver, self, result["state"]),
        )

        driver_ready.set()

        self._logger.info(
            "Z-Wave JS initialized. %s nodes", len(self.driver.controller.nodes)
        )

    def _check_server_version(self, server_version: str) -> None:
        """Perform a basic check on the server version compatability."""
        cur_version = parse_version(server_version)
        min_version = parse_version(MIN_SERVER_VERSION)
        if cur_version < min_version:
            raise InvalidServerVersion
        if cur_version != min_version:
            self._logger.warning(
                "Connected to a Zwave JS Server with an untested version, \
                    you may run into compatibility issues!"
            )

    def _handle_incoming_message(self, msg: dict) -> None:
        """Handle incoming message.

        Run all async tasks in a wrapper to log appropriately.
        """
        if msg["type"] == "result":
            future = self._result_futures.get(msg["messageId"])

            if future is None:
                self._logger.warning(
                    "Received result for unknown message with ID: %s", msg["messageId"]
                )
                return

            if msg["success"]:
                future.set_result(msg["result"])
                return

            future.set_exception(FailedCommand(msg["messageId"], msg["errorCode"]))
            return

        # Cannot happen but testing just in case.
        if self.driver is None:
            self._logger.error(
                "Did not receive state as first message. Closing connection."
            )
            asyncio.create_task(self._client.close())

        if msg["type"] != "event":
            # Can't handle
            self._logger.debug(
                "Received message with unknown type '%s': %s",
                msg["type"],
                msg,
            )
            return

        event = Event(type=msg["event"]["event"], data=msg["event"])
        self.driver.receive_event(event)

    async def _send_json_message(self, message: Dict[str, Any]) -> None:
        """Send a message.

        Raises NotConnected if client not connected.
        """
        if self.state != STATE_CONNECTED:
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
