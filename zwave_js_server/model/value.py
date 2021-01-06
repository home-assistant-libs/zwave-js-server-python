"""Value model."""


from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .node import Node


def value_id(node: "Node", event: dict) -> str:
    """Return ID of value."""
    command_class = event.get("commandClass")
    endpoint = event.get("endpoint")
    property_key_name = event.get("propertyKeyName")
    return f"{node.node_id}-{command_class}-{endpoint}-{property_key_name}"


class ValueMetadata:
    def __init__(self, data) -> None:
        self.data = data

    @property
    def type(self) -> str:
        """Return type."""
        return self.data.get("type")

    @property
    def readable(self) -> str:
        """Return readable."""
        return self.data.get("readable")

    @property
    def writeable(self) -> str:
        """Return writeable."""
        return self.data.get("writeable")

    @property
    def label(self) -> str:
        """Return label."""
        return self.data.get("label")


class Value:
    def __init__(self, node: "Node", added_event: dict) -> None:
        self.node = node
        self.data = added_event

    @property
    def value_id(self) -> str:
        return value_id(self.node, self.data)

    # Only included in initial state dump which can't be used yet
    # @property
    # def metadata(self) -> ValueMetadata:
    #     return ValueMetadata(self.data["metadata"])

    @property
    def value(self) -> Any:
        return self.data.get("newValue")

    @property
    def command_class_name(self) -> str:
        """Return commandClassName."""
        return self.data.get("commandClassName")

    @property
    def command_class(self) -> int:
        """Return commandClass."""
        return self.data.get("commandClass")

    @property
    def endpoint(self) -> int:
        """Return endpoint."""
        return self.data.get("endpoint")

    # TODO Invalid Python. Decide on proper name.
    # @property
    # def property(self) -> str:
    #     """Return property."""
    #     return self.data.get("property")

    @property
    def property_key(self) -> str:
        """Return propertyKey."""
        return self.data.get("propertyKey")

    @property
    def property_name(self) -> str:
        """Return propertyName."""
        return self.data.get("propertyName")

    @property
    def property_key_name(self) -> str:
        """Return propertyKeyName."""
        return self.data.get("propertyKeyName")

    def receive_event(self, event: dict):
        """Receive an event."""
        if event["event"] != "value updated":
            return

        self.data = event
