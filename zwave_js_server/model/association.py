"""Provide a model for the association."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AssociationGroup:
    """Represent a association group dict type."""

    max_nodes: int
    is_lifeline: bool
    multi_channel: bool
    label: str
    profile: Optional[int] = None
    issued_commands: Dict[int, List[int]] = field(default_factory=dict)


@dataclass
class Association:
    """Represent a association dict type."""

    node_id: int
    endpoint: Optional[int] = None
