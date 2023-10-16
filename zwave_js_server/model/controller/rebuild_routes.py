"""Provide models for rebuilding routes."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypedDict


class RebuildRoutesOptionsDataType(TypedDict, total=False):
    """Represent a rebuild routes options data dict type."""

    includeSleeping: bool


@dataclass
class RebuildRoutesOptions:
    """Represent options for rebuilding routes."""

    include_sleeping: bool | None = None

    @classmethod
    def from_dict(cls, data: RebuildRoutesOptionsDataType) -> RebuildRoutesOptions:
        """Return options from data."""
        return cls(include_sleeping=data.get("includeSleeping"))

    def to_dict(self) -> RebuildRoutesOptionsDataType:
        """Return dict representation of data."""
        if self.include_sleeping is None:
            return {}
        return {"includeSleeping": self.include_sleeping}


class RebuildRoutesStatus(StrEnum):
    """Enum of all known rebuild routes status values."""

    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"
