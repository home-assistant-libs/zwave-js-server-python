"""Client."""
import asyncio
import logging
import pprint
import uuid
from types import TracebackType
from typing import Any, Awaitable, Callable, Dict, List, Optional, cast

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType, client_exceptions
from packaging.version import parse as parse_version

from .const import MIN_SERVER_VERSION
from .event import Event
from .exceptions import (
    CannotConnect,
    ConnectionClosed,
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


async def gather_callbacks(
    logger: logging.Logger, name: str, callbacks: List[Callable[[], Awaitable[None]]]
) -> None:
    """Gather callbacks."""
    results = await asyncio.gather(*[cb() for cb in callbacks], return_exceptions=True)
    for result, callback in zip(results, callbacks):
        if not isinstance(result, Exception):
            continue
        logger.error("Unexpected error in %s %s", name, callback, exc_info=result)


class Client:
    """Class to manage the IoT connection."""

    def __init__(
        self,
        ws_server_url: str,
        aiohttp_session: ClientSession,
        *,
        start_listening_on_connect: bool = True,
    ):
        """Initialize the Client class."""
        self.ws_server_url = ws_server_url
        self.aiohttp_session = aiohttp_session
        self.driver: Optional[Driver] = None
        # The WebSocket client
        self.client: Optional[ClientWebSocketResponse] = None
        # Current state of the connection
        self.state = STATE_DISCONNECTED
        # Version of the connected server
        self.version: Optional[VersionInfo] = None
        self._on_connect: List[Callable[[], Awaitable[None]]] = []
        self._on_disconnect: List[Callable[[], Awaitable[None]]] = []
        self._on_initialized: List[Callable[[], Awaitable[None]]] = []
        self._logger = logging.getLogger(__package__)
        self._loop = asyncio.get_running_loop()
        self._result_futures: Dict[str, asyncio.Future] = {}

        if start_listening_on_connect:
            self.register_on_connect(self._start_listening)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{type(self).__name__}(ws_server_url={self.ws_server_url!r})"

    def async_handle_message(self, msg: dict) -> None:
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

        if self.driver is None:
            raise InvalidState("Did not receive state as first message")

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

    def register_on_connect(
        self, on_connect_cb: Callable[[], Awaitable[None]]
    ) -> Callable:
        """Register an async on_connect callback."""

        def unsubscribe() -> None:
            """Unsubscribe listeners."""
            if on_connect_cb in self._on_connect:
                self._on_connect.remove(on_connect_cb)

        self._on_connect.append(on_connect_cb)
        return unsubscribe

    def register_on_disconnect(
        self, on_disconnect_cb: Callable[[], Awaitable[None]]
    ) -> Callable:
        """Register an async on_disconnect callback."""

        def unsubscribe() -> None:
            """Unsubscribe listeners."""
            if on_disconnect_cb in self._on_disconnect:
                self._on_disconnect.remove(on_disconnect_cb)

        self._on_disconnect.append(on_disconnect_cb)
        return unsubscribe

    def register_on_initialized(
        self, on_initialized_cb: Callable[[], Awaitable[None]]
    ) -> Callable:
        """Register an async on_initialized_cb callback."""

        def unsubscribe() -> None:
            """Unsubscribe listeners."""
            if on_initialized_cb in self._on_initialized:
                self._on_initialized.remove(on_initialized_cb)

        self._on_initialized.append(on_initialized_cb)
        return unsubscribe

    @property
    def connected(self) -> bool:
        """Return if we're currently connected."""
        return self.state == STATE_CONNECTED

    async def async_send_command(self, message: Dict[str, Any]) -> dict:
        """Send a command and get a response."""
        future: "asyncio.Future[dict]" = self._loop.create_future()
        message_id = message["messageId"] = uuid.uuid4().hex
        self._result_futures[message_id] = future
        await self.async_send_json_message(message)
        try:
            return await future
        finally:
            self._result_futures.pop(message_id)

    async def async_send_json_message(self, message: Dict[str, Any]) -> None:
        """Send a message.

        Raises NotConnected if client not connected.
        """
        if self.state != STATE_CONNECTED:
            raise NotConnected

        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("Publishing message:\n%s\n", pprint.pformat(message))

        assert self.client
        if "messageId" not in message:
            message["messageId"] = uuid.uuid4().hex
        await self.client.send_json(message)

    async def connect(self) -> None:
        """Connect to the websocket server."""
        client = None
        self._logger.debug("Trying to connect")
        try:
            self.client = client = await self.aiohttp_session.ws_connect(
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

        if self._on_connect:
            asyncio.create_task(
                gather_callbacks(self._logger, "on_connect", self._on_connect)
            )

    async def listen(self) -> None:
        """Start listening to the websocket."""
        assert self.client

        while not self.client.closed:
            try:
                msg = await self.client.receive()
            except asyncio.CancelledError:
                break

            if msg.type in (WSMsgType.CLOSED, WSMsgType.CLOSING):
                break

            if msg.type == WSMsgType.CLOSE:
                raise ConnectionClosed()

            if msg.type == WSMsgType.ERROR:
                raise ConnectionFailed()

            if msg.type != WSMsgType.TEXT:
                raise InvalidMessage(f"Received non-Text message: {msg.type}")

            try:
                if len(msg.data) > SIZE_PARSE_JSON_EXECUTOR:
                    msg = await self._loop.run_in_executor(None, msg.json)
                else:
                    msg = msg.json()
            except ValueError as err:
                raise InvalidMessage("Received invalid JSON.") from err

            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Received message:\n%s\n", pprint.pformat(msg))

            msg_ = cast(dict, msg)

            try:
                self.async_handle_message(msg_)
            except InvalidState:
                await self._close()
                raise

    async def disconnect(self) -> None:
        """Disconnect the client."""
        if self.client is not None:
            await self._close()

        self.state = STATE_DISCONNECTED

        if self._on_disconnect:
            asyncio.create_task(
                gather_callbacks(self._logger, "on_disconnect", self._on_disconnect)
            )

    async def _close(self) -> None:
        """Close the client connection."""
        self._logger.debug("Closing client connection")
        assert self.client
        await self.client.close()
        self.driver = None

    async def _start_listening(self) -> None:
        """When connected, start listening."""
        result = await self.async_send_command({"command": "start_listening"})

        if self.driver is not None:
            raise InvalidState("Re-connected with existing driver")

        self.driver = cast(
            Driver,
            await self._loop.run_in_executor(None, Driver, self, result["state"]),
        )
        self._logger.info(
            "Z-Wave JS initialized. %s nodes", len(self.driver.controller.nodes)
        )
        asyncio.create_task(
            gather_callbacks(self._logger, "on_initialized", self._on_initialized)
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

    async def __aenter__(self) -> "Client":
        """Connect to the websocket."""
        await self.connect()
        return self

    async def __aexit__(
        self, exc_type: Exception, exc_value: str, traceback: TracebackType
    ) -> None:
        """Disconnect from the websocket."""
        await self.disconnect()
