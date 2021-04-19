"""Provide a model for a log message event."""
from typing import List, Literal, Optional, TypedDict, Union


class LogMessageDataType(TypedDict, total=False):
    """Represent a log message data dict type."""

    source: Literal["driver"]  # required
    event: Literal["logging"]  # required
    message: Union[str, List[str]]  # required
    formattedMessage: Union[str, List[str]]  # required
    direction: str  # required
    level: str  # required
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
        self, field_name: Union[Literal["message"], Literal["formattedMessage"]]
    ) -> List[str]:
        """Process a message and always return a list."""
        if isinstance(self.data[field_name], str):
            return str(self.data[field_name]).splitlines()

        # We will assume each item in the array is on a separate line so we can
        # remove trailing line breaks
        return [message.rstrip("\n") for message in self.data[field_name]]

    @property
    def message(self) -> List[str]:
        """Return message."""
        return self._process_message("message")

    @property
    def formatted_message(self) -> List[str]:
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
    def primary_tags(self) -> Optional[str]:
        """Return primary tags."""
        return self.data.get("primaryTags")

    @property
    def secondary_tags(self) -> Optional[str]:
        """Return secondary tags."""
        return self.data.get("secondaryTags")

    @property
    def secondary_tag_padding(self) -> Optional[int]:
        """Return secondary tag padding."""
        return self.data.get("secondaryTagPadding")

    @property
    def multiline(self) -> Optional[bool]:
        """Return whether message is multiline."""
        return self.data.get("multiline")

    @property
    def timestamp(self) -> Optional[str]:
        """Return timestamp."""
        return self.data.get("timestamp")

    @property
    def label(self) -> Optional[str]:
        """Return label."""
        return self.data.get("label")
