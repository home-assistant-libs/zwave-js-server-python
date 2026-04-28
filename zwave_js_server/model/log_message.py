"""Provide a model for a log message event."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict

from ..const import CommandClass


class LogMessageContextDataType(TypedDict, total=False):
    """Represent a log message context data dict type."""

    source: Literal["config", "serial", "controller", "driver"]  # required
    type: Literal["controller", "value", "node"]
    nodeId: int
    header: str
    direction: Literal["inbound", "outbound", "none"]
    change: Literal["added", "removed", "updated", "notification"]
    internal: bool
    endpoint: int
    commandClass: int
    property: int | str
    propertyKey: int | str


@dataclass(frozen=True)
class LogMessageContext:
    """Represent log message context information."""

    data: LogMessageContextDataType = field(repr=False)
    source: Literal["config", "serial", "controller", "driver"] = field(init=False)
    type: Literal["controller", "value", "node"] | None = field(init=False)
    node_id: int | None = field(init=False)
    header: str | None = field(init=False)
    direction: Literal["inbound", "outbound", "none"] | None = field(init=False)
    change: Literal["added", "removed", "updated", "notification"] | None = field(
        init=False
    )
    internal: bool | None = field(init=False)
    endpoint: int | None = field(init=False)
    command_class: CommandClass | None = field(init=False, default=None)
    property_: int | str | None = field(init=False)
    property_key: int | str | None = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        object.__setattr__(self, "source", self.data["source"])
        object.__setattr__(self, "type", self.data.get("type"))
        object.__setattr__(self, "node_id", self.data.get("nodeId"))
        object.__setattr__(self, "header", self.data.get("header"))
        object.__setattr__(self, "direction", self.data.get("direction"))
        object.__setattr__(self, "change", self.data.get("change"))
        object.__setattr__(self, "internal", self.data.get("internal"))
        object.__setattr__(self, "endpoint", self.data.get("endpoint"))
        if (command_class := self.data.get("commandClass")) is not None:
            object.__setattr__(self, "command_class", CommandClass(command_class))
        object.__setattr__(self, "property_", self.data.get("property"))
        object.__setattr__(self, "property_key", self.data.get("propertyKey"))


class LogMessageDataType(TypedDict, total=False):
    """Represent a log message data dict type."""

    source: Literal["driver"]  # required
    event: Literal["logging"]  # required
    message: str | list[str]  # required
    formattedMessage: str | list[str]  # required
    direction: str  # required
    level: str  # required
    context: LogMessageContextDataType  # required
    primaryTags: str
    secondaryTags: str
    secondaryTagPadding: int
    multiline: bool
    timestamp: str
    label: str


def _process_message(message: str | list[str]) -> list[str]:
    """Process a message and always return a list."""
    if isinstance(message, str):
        return str(message).splitlines()

    # We will assume each item in the array is on a separate line so we can
    # remove trailing line breaks
    return [message.rstrip("\n") for message in message]


@dataclass(frozen=True)
class LogMessage:
    """Represent a log message."""

    data: LogMessageDataType = field(repr=False)
    message: list[str] = field(init=False)
    formatted_message: list[str] = field(init=False)
    direction: str = field(init=False)
    level: str = field(init=False)
    context: LogMessageContext = field(init=False)
    primary_tags: str | None = field(init=False)
    secondary_tags: str | None = field(init=False)
    secondary_tag_padding: int | None = field(init=False)
    multiline: bool | None = field(init=False)
    timestamp: str | None = field(init=False)
    label: str | None = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        object.__setattr__(self, "message", _process_message(self.data["message"]))
        object.__setattr__(
            self, "formatted_message", _process_message(self.data["formattedMessage"])
        )
        object.__setattr__(self, "direction", self.data["direction"])
        object.__setattr__(self, "level", self.data["level"])
        object.__setattr__(self, "context", LogMessageContext(self.data["context"]))
        object.__setattr__(self, "primary_tags", self.data.get("primaryTags"))
        object.__setattr__(self, "secondary_tags", self.data.get("secondaryTags"))
        object.__setattr__(
            self, "secondary_tag_padding", self.data.get("secondaryTagPadding")
        )
        object.__setattr__(self, "multiline", self.data.get("multiline"))
        object.__setattr__(self, "timestamp", self.data.get("timestamp"))
        object.__setattr__(self, "label", self.data.get("label"))
