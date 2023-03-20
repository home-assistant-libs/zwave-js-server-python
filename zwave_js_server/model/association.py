"""Provide a model for the association."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AssociationGroup:
    """Represent a association group dict type."""

    max_nodes: int
    is_lifeline: bool
    multi_channel: bool
    label: str
    profile: int | None = None
    issued_commands: dict[int, list[int]] = field(default_factory=dict)


@dataclass
class AssociationAddress:
    """Represent a association dict type."""

    node_id: int
    endpoint: int | None = None
