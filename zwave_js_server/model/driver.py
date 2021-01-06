"""Z-Wave JS Driver."""
from .controller import Controller
from ..event import EventBase


class Driver(EventBase):
    def __init__(self, state: dict):
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
