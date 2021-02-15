"""Provide a model for the Z-Wave JS Driver."""
import dataclasses
from typing import TYPE_CHECKING, cast
from zwave_js_server.model.log_config import LogConfig

from ..event import Event, EventBase
from ..helpers import snake_to_camel_case
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

    def receive_event(self, event: Event) -> None:
        """Receive an event."""
        if event.data["source"] != "driver":
            self.controller.receive_event(event)
            return

        self._handle_event_protocol(event)

        self.emit(event.type, event.data)

    def handle_all_nodes_ready(self, event: Event) -> None:
        """Process a driver all nodes ready event."""

    async def async_update_log_config(self, log_config: LogConfig) -> bool:
        """Update log config for driver."""
        result = await self.client.async_send_command(
            {
                "command": "update_log_config",
                "config": {
                    snake_to_camel_case(field.name): getattr(log_config, field.name)
                    for field in dataclasses.fields(log_config)
                    if getattr(log_config, field.name) is not None
                },
            }
        )

        return cast(bool, result["success"])
