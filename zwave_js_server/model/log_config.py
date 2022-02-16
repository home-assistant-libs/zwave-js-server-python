"""Provide a model for the log config."""
from dataclasses import dataclass
from typing import Optional, cast

from ..const import TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED, LogLevel

if TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED:
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


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
    enabled: Optional[bool] = None
    level: Optional[LogLevel] = None
    log_to_file: Optional[bool] = None
    filename: Optional[str] = None
    force_console: Optional[bool] = None

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
    def from_dict(cls, data: LogConfigDataType) -> "LogConfig":
        """Return LogConfig from LogConfigDataType dict."""
        return cls(
            data.get("enabled"),
            LogLevel(data["level"]) if "level" in data else None,
            data.get("logToFile"),
            data.get("filename"),
            data.get("forceConsole"),
        )
