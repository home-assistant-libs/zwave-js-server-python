"""Provide a model for the Z-Wave JS Driver."""
from typing import cast

from ..event import Event, EventBase
from ..protocol import ProtocolType, driver as protocol, get_handler
from .controller import Controller


class Driver(EventBase):
    """Represent a Z-Wave JS driver."""

    def __init__(self, state: dict):
        """Initialize driver."""
        super().__init__()
        self.controller = Controller(state)

    def receive_event(self, event: Event) -> None:
        """Receive an event."""
        if event.data["source"] != "driver":
            self.controller.receive_event(event)
            return

        protocol_ = cast(ProtocolType, protocol)
        event_handler = get_handler(protocol_, event)
        event_handler(self, event)

        self.emit(event.data["event"], event.data)
