"""Provide a model for a log message event."""
from __future__ import annotations

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


class LogMessageContext:
    """Represent log message context information."""

    def __init__(self, data: LogMessageContextDataType) -> None:
        """Initialize log message context."""
        self.data = data

    @property
    def source(self) -> Literal["config", "serial", "controller", "driver"]:
        """Return the log message source."""
        return self.data["source"]

    @property
    def type(self) -> Literal["controller", "value", "node"] | None:
        """Return the object type for the log message if applicable."""
        return self.data.get("type")

    @property
    def node_id(self) -> int | None:
        """Return the Node ID for the log message if applicable."""
        return self.data.get("nodeId")

    @property
    def header(self) -> str | None:
        """Return the header for the log message if applicable."""
        return self.data.get("header")

    @property
    def direction(self) -> Literal["inbound", "outbound", "none"] | None:
        """Return the direction for the log message if applicable."""
        return self.data.get("direction")

    @property
    def change(
        self,
    ) -> Literal["added", "removed", "updated", "notification"] | None:
        """Return the change type for the log message if applicable."""
        return self.data.get("change")

    @property
    def internal(self) -> bool | None:
        """Return the internal flag for the log message if applicable."""
        return self.data.get("internal")

    @property
    def endpoint(self) -> int | None:
        """Return the Node/Value endpoint for the log message if applicable."""
        return self.data.get("endpoint")

    @property
    def command_class(self) -> CommandClass | None:
        """Return the Value command class for the log message if applicable."""
        if command_class := self.data.get("commandClass"):
            return CommandClass(command_class)
        return None

    @property
    def property_(self) -> int | str | None:
        """Return the Value property for the log message if applicable."""
        return self.data.get("property")

    @property
    def property_key(self) -> int | str | None:
        """Return the Value property key for the log message if applicable."""
        return self.data.get("propertyKey")


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


class LogMessage:
    """Represent a log message."""

    def __init__(self, data: LogMessageDataType):
        """Initialize log message."""
        self.data = data

    def _process_message(
        self, field_name: Literal["message", "formattedMessage"]
    ) -> list[str]:
        """Process a message and always return a list."""
        if isinstance(self.data[field_name], str):
            return str(self.data[field_name]).splitlines()

        # We will assume each item in the array is on a separate line so we can
        # remove trailing line breaks
        return [message.rstrip("\n") for message in self.data[field_name]]

    @property
    def message(self) -> list[str]:
        """Return message."""
        return self._process_message("message")

    @property
    def formatted_message(self) -> list[str]:
        """Return fully formatted message."""
        return self._process_message("formattedMessage")

    @property
    def direction(self) -> str:
        """Return direction."""
        return self.data["direction"]

    @property
    def level(self) -> str:
        """Return level."""
        return self.data["level"]

    @property
    def primary_tags(self) -> str | None:
        """Return primary tags."""
        return self.data.get("primaryTags")

    @property
    def secondary_tags(self) -> str | None:
        """Return secondary tags."""
        return self.data.get("secondaryTags")

    @property
    def secondary_tag_padding(self) -> int | None:
        """Return secondary tag padding."""
        return self.data.get("secondaryTagPadding")

    @property
    def multiline(self) -> bool | None:
        """Return whether message is multiline."""
        return self.data.get("multiline")

    @property
    def timestamp(self) -> str | None:
        """Return timestamp."""
        return self.data.get("timestamp")

    @property
    def label(self) -> str | None:
        """Return label."""
        return self.data.get("label")

    @property
    def context(self) -> LogMessageContext:
        """Return context."""
        return LogMessageContext(self.data["context"])
