"""Provide a model for the websocket message."""
from dataclasses import dataclass, field

from ..exceptions import InvalidMessageError


@dataclass
class Message:
    """Represent a websocket message."""

    type: str
    data: dict = field(default_factory=dict)

    @classmethod
    def from_data(cls, data: dict) -> "Message":
        """Create a Message instance from a json websocket message."""
        # TODO: Convince zwave-js-server JS to
        # unify event and state to a single attribute: data.
        if data["type"] == "event":
            message_data = data["event"]
        elif data["type"] == "state":
            message_data = data["state"]
        else:
            raise InvalidMessageError

        return cls(data["type"], message_data)
