"""Provide a model for the log config."""
from dataclasses import dataclass
from typing import Optional

from ..const import LogLevel


@dataclass
class LogConfig:
    """Represent a log config dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/core/src/log/shared.ts#L85
    # Must include at least one key
    # TODO: Is support for `transports` needed? If so, add support
    enabled: Optional[bool] = None
    level: Optional[LogLevel] = None
    log_to_file: Optional[bool] = None
    filename: Optional[str] = None
    force_console: Optional[bool] = None
