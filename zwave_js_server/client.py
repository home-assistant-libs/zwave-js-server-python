"""Client."""
import asyncio
import logging
import pprint
import random
from typing import Awaitable, Callable, List

from aiohttp import ClientSession, WSMsgType, client_exceptions

from .model.driver import Driver

STATE_CONNECTING = "connecting"
STATE_CONNECTED = "connected"
STATE_DISCONNECTED = "disconnected"


async def gather_callbacks(
    logger: logging.Logger, name: str, callbacks: List[Callable[[], Awaitable[None]]]
) -> None:
    results = await asyncio.gather(*[cb() for cb in callbacks], return_exceptions=True)
    for result, callback in zip(results, callbacks):
        if not isinstance(result, Exception):
            continue
        logger.error("Unexpected error in %s %s", name, callback, exc_info=result)


class NotConnected(Exception):
    """Exception raised when trying to handle unknown handler."""


class InvalidState(Exception):
    """Exception raised when data gets in invalid state."""


class Client:
    """Class to manage the IoT connection."""

    def __init__(self, ws_server_url: str, aiohttp_session: ClientSession):
        """Initialize the Client class."""
        self.ws_server_url = ws_server_url
        self.aiohttp_session = aiohttp_session
        self.driver = None
        # The WebSocket client
        self.client = None
        # Scheduled sleep task till next connection retry
        self.retry_task = None
        # Boolean to indicate if we wanted the connection to close
        self.close_requested = False
        # The current number of attempts to connect, impacts wait time
        self.tries = 0
        # Current state of the connection
        self.state = STATE_DISCONNECTED
        self._on_connect: List[Callable[[], Awaitable[None]]] = []
        self._on_disconnect: List[Callable[[], Awaitable[None]]] = []
        self._on_initialized: List[Callable[[], Awaitable[None]]] = []
        self._logger = logging.getLogger(__package__)
        self._disconnect_event = None

    def async_handle_message(self, msg) -> None:
        """Handle incoming message.
        Run all async tasks in a wrapper to log appropriately.
        """
        if msg["type"] == "state":
            if self.driver is None:
                self.driver = Driver(msg["state"])
                self._logger.info(
                    "Z-Wave JS initialized. %s nodes", len(self.driver.controller.nodes)
                )
                await gather_callbacks(self._logger, "on_initialized", self._on_initialized)
            else:
                # TODO how do we handle reconnect?
                pass

            return

        if self.driver is None:
            raise InvalidState("Did not receive state as first message")

        if msg["type"] != "event":
            # Can't handle
            return

        self.driver.receive_event(msg["event"])

    def register_on_connect(self, on_connect_cb: Callable[[], Awaitable[None]]):
        """Register an async on_connect callback."""
        self._on_connect.append(on_connect_cb)

    def register_on_disconnect(self, on_disconnect_cb: Callable[[], Awaitable[None]]):
        """Register an async on_disconnect callback."""
        self._on_disconnect.append(on_disconnect_cb)

    def register_on_initialized(self, on_initialized_cb: Callable[[], Awaitable[None]]):
        """Register an async on_initialized_cb callback."""
        self._on_initialized.append(on_initialized_cb)

    @property
    def connected(self):
        """Return if we're currently connected."""
        return self.state == STATE_CONNECTED

    async def async_send_json_message(self, message):
        """Send a message.

        Raises NotConnected if client not connected.
        """
        if self.state != STATE_CONNECTED:
            raise NotConnected

        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("Publishing message:\n%s\n", pprint.pformat(message))

        await self.client.send_json(message)

    async def connect(self):
        """Connect to the IoT broker."""
        if self.state != STATE_DISCONNECTED:
            raise RuntimeError("Connect called while not disconnected")

        self.close_requested = False
        self.state = STATE_CONNECTING
        self.tries = 0
        self._disconnect_event = asyncio.Event()

        while True:
            try:
                self._logger.debug("Trying to connect")
                await self._handle_connection()
            except Exception:  # pylint: disable=broad-except
                # Safety net. This should never hit.
                # Still adding it here to make sure we can always reconnect
                self._logger.exception("Unexpected error")

            if self.state == STATE_CONNECTED and self._on_disconnect:
                await gather_callbacks(
                    self._logger, "on_disconnect", self._on_disconnect
                )

            if self.close_requested:
                break

            self.state = STATE_CONNECTING
            self.tries += 1

            try:
                await self._wait_retry()
            except asyncio.CancelledError:
                # Happens if disconnect called
                break

        self.state = STATE_DISCONNECTED
        self._disconnect_event.set()
        self._disconnect_event = None

    async def _wait_retry(self):
        """Wait until it's time till the next retry."""
        # Sleep 2^tries + 0…tries*3 seconds between retries
        self.retry_task = asyncio.create_task(
            asyncio.sleep(2 ** min(9, self.tries) + random.randint(0, self.tries * 3))
        )
        await self.retry_task
        self.retry_task = None

    async def _handle_connection(self):
        """Connect to the Z-Wave JS server."""
        client = None
        disconnect_warn = None
        try:
            self.client = client = await self.aiohttp_session.ws_connect(
                self.ws_server_url,
                heartbeat=55,
            )
            self.tries = 0

            self._logger.info("Connected")
            self.state = STATE_CONNECTED

            if self._on_connect:
                await gather_callbacks(self._logger, "on_connect", self._on_connect)

            while not client.closed:
                msg = await client.receive()

                if msg.type in (WSMsgType.CLOSED, WSMsgType.CLOSING):
                    break

                if msg.type == WSMsgType.ERROR:
                    disconnect_warn = "Connection error"
                    break

                if msg.type != WSMsgType.TEXT:
                    disconnect_warn = "Received non-Text message: {}".format(msg.type)
                    break

                try:
                    msg = msg.json()
                except ValueError:
                    disconnect_warn = "Received invalid JSON."
                    break

                if self._logger.isEnabledFor(logging.DEBUG):
                    self._logger.debug("Received message:\n%s\n", pprint.pformat(msg))

                try:
                    self.async_handle_message(msg)

                except InvalidState as err:
                    disconnect_warn = f"Invalid state: {err}"
                    await client.close()
                    break

                except Exception:  # pylint: disable=broad-except
                    self._logger.exception("Unexpected error handling %s", msg)
                    break

        except client_exceptions.WSServerHandshakeError as err:
            self._logger.warning("Unable to connect: %s", err)

        except client_exceptions.ClientError as err:
            self._logger.warning("Unable to connect: %s", err)

        except asyncio.CancelledError:
            pass

        finally:
            if disconnect_warn is None:
                self._logger.info("Connection closed")
            else:
                self._logger.warning("Connection closed: %s", disconnect_warn)

    async def disconnect(self):
        """Disconnect the client."""
        self.close_requested = True

        if self.client is not None:
            await self.client.close()
        elif self.retry_task is not None:
            self.retry_task.cancel()

        if self._disconnect_event is not None:
            await self._disconnect_event.wait()
