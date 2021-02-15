"""Provide a model for the log config."""
from typing import TypedDict

from ..const import LogLevel


class LogConfig(TypedDict, total=False):
    """Represent a log config dict type."""

    # TODO: Is support for `transports` needed? If so, add support
    # Must include at least one key
    enabled: bool
    level: LogLevel
    logToFile: bool
    filename: str
    forceConsole: bool
