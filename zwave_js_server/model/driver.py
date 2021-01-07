"""Provide a model for the Z-Wave JS driver."""
from .controller import Controller
from ..event import EventBase


class Driver(EventBase):
    """Represent a Z-Wave JS driver."""

    def __init__(self, state: dict):
        """Initialize driver."""
        super().__init__()
        self.controller = Controller(state)

    def receive_event(self, event: dict):
        """Receive an event."""
        if event["source"] != "driver":
            self.controller.receive_event(event)
            return

        if event["event"] == "all nodes ready":
            pass

        self.emit(event["event"], event)
