"""Provide a model for the Z-Wave JS Driver."""
from ..event import Event, EventBase
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

        self._handle_event_protocol(event)

        self.emit(event.type, event.data)

    def handle_all_nodes_ready(self, event: Event) -> None:
        """Process a driver all nodes ready event."""
