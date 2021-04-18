"""Provide a model for the Z-Wave JS Driver."""
from typing import TYPE_CHECKING
from zwave_js_server.model.log_message import LogMessage

from zwave_js_server.model.log_config import LogConfig

from ..event import Event, EventBase
from .controller import Controller

if TYPE_CHECKING:
    from ..client import Client


class Driver(EventBase):
    """Represent a Z-Wave JS driver."""

    def __init__(self, client: "Client", state: dict) -> None:
        """Initialize driver."""
        super().__init__()
        self.client = client
        self.controller = Controller(client, state)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.controller)

    def __eq__(self, other: object) -> bool:
        """Return whether this instance equals another."""
        if not isinstance(other, Driver):
            return False
        return self.controller == other.controller

    def receive_event(self, event: Event) -> None:
        """Receive an event."""
        if event.data["source"] != "driver":
            self.controller.receive_event(event)
            return

        self._handle_event_protocol(event)

        self.emit(event.type, event.data)

    def handle_logging(self, event: Event) -> None:
        """Process a driver logging event."""
        event.data["log_message"] = LogMessage(event.data)

    def handle_all_nodes_ready(self, event: Event) -> None:
        """Process a driver all nodes ready event."""

    async def async_send_command(self, command: str, **kwargs) -> dict:
        """Send a driver command."""
        return await self.client.async_send_command(
            {
                "command": f"driver.{command}",
                **kwargs,
            }
        )

    async def async_update_log_config(self, log_config: LogConfig) -> None:
        """Update log config for driver."""
        await self.async_send_command("update_log_config", config=log_config.to_dict())

    async def async_get_log_config(self) -> LogConfig:
        """Return current log config for driver."""
        result = await self.async_send_command("get_log_config")
        return LogConfig.from_dict(result["config"])

    async def async_start_listening_to_logs(self) -> None:
        """Send command to start listening to logs."""
        await self.async_send_command("start_listening_to_logs")

    async def async_stop_listening_to_logs(self) -> None:
        """Send command to stop listening to logs."""
        await self.async_send_command("stop_listening_to_logs")
