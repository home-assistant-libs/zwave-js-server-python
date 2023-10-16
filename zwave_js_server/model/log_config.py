"""Provide a model for the log config."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict, cast

from ..const import LogLevel


class LogConfigDataType(TypedDict, total=False):
    """Represent a log config data dict type."""

    enabled: bool
    level: str
    logToFile: bool
    filename: str
    forceConsole: bool


@dataclass
class LogConfig:
    """Represent a log config dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/core/src/log/shared.ts#L85
    # Must include at least one key
    enabled: bool | None = None
    level: LogLevel | None = None
    log_to_file: bool | None = None
    filename: str | None = None
    force_console: bool | None = None

    def to_dict(self) -> LogConfigDataType:
        """Return LogConfigDataType dict from self."""
        data = {
            "enabled": self.enabled,
            "level": self.level.value if self.level else None,
            "logToFile": self.log_to_file,
            "filename": self.filename,
            "forceConsole": self.force_console,
        }
        return cast(LogConfigDataType, {k: v for k, v in data.items() if v is not None})

    @classmethod
    def from_dict(cls, data: LogConfigDataType) -> LogConfig:
        """Return LogConfig from LogConfigDataType dict."""
        return cls(
            data.get("enabled"),
            LogLevel(data["level"]) if "level" in data else None,
            data.get("logToFile"),
            data.get("filename"),
            data.get("forceConsole"),
        )
