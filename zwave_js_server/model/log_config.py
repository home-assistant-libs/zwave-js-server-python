"""Provide a model for the log config."""
from dataclasses import dataclass
from typing import Optional

from ..const import LogLevel


@dataclass
class LogConfig:
    """Represent a log config dict type."""

    # TODO: Is support for `transports` needed? If so, add support
    # Must include at least one key
    enabled: Optional[bool] = None
    level: Optional[LogLevel] = None
    log_to_file: Optional[bool] = None
    filename: Optional[str] = None
    force_console: Optional[bool] = None
