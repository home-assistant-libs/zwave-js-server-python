"""Provide a model for the log config."""
from dataclasses import dataclass

from ..const import LogLevel


@dataclass
class LogConfig:
    """Represent a log config dict type."""

    # TODO: Is support for `transports` needed? If so, add support
    # Must include at least one key
    enabled: bool
    level: LogLevel
    logToFile: bool
    filename: str
    forceConsole: bool
