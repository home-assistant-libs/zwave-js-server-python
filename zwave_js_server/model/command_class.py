"""
Model for Zwave Command Class Info.

https://zwave-js.github.io/node-zwave-js/#/api/endpoint?id=commandclasses
"""
from __future__ import annotations

from typing import TypedDict

from ..const import CommandClass


class CommandClassInfoDataType(TypedDict):
    """Represent a command class info data dict type."""

    id: int
    name: str
    version: int
    isSecure: bool


class CommandClassInfo:
    """Model for a Zwave CommandClass Info."""

    def __init__(self, data: CommandClassInfoDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def id(self) -> int:
        """Return CommandClass ID."""
        return self.data["id"]

    @property
    def command_class(self) -> CommandClass:
        """Return CommandClass."""
        return CommandClass(self.id)

    @property
    def name(self) -> str:
        """Return friendly name for CommandClass."""
        return self.data["name"]

    @property
    def version(self) -> int:
        """Return the CommandClass version used on this node/endpoint."""
        return self.data["version"]

    @property
    def is_secure(self) -> bool:
        """Return if the CommandClass is used securely on this node/endpoint."""
        return self.data["isSecure"]
