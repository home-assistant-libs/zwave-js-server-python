"""Provide a model for the Z-Wave JS driver."""
from dataclasses import dataclass, field
from typing import cast

from ..event import EventBase
from ..protocol import ProtocolType, driver as protocol, get_handler
from .controller import Controller, ControllerEvent


@dataclass
class DriverEvent:
    """Represent a Driver event."""

    type: str
    data: dict = field(default_factory=dict)


class Driver(EventBase):
    """Represent a Z-Wave JS driver."""

    def __init__(self, state: dict):
        """Initialize driver."""
        super().__init__()
        self.controller = Controller(state)

    def handle_event(self, event: DriverEvent) -> None:
        """Handle a zwave-js event."""
        if event.data["source"] != "driver":
            controller_event = ControllerEvent(
                type=event.data["event"], data=event.data
            )
            self.controller.handle_event(controller_event)
            return

        protocol_ = cast(ProtocolType, protocol)
        event_handler = get_handler(protocol_, event)
        event_handler(self, event)

        self.emit(event.data["event"], event.data)
