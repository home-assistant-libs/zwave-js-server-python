"""Provide a model for the association."""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AssociationGroup:
    """Represent a association group dict type."""

    max_nodes: int
    is_lifeline: bool
    multi_channel: bool
    label: str
    profile: Optional[int] = None
    issued_commands: Optional[Dict[int, List[int]]] = None


@dataclass
class Association:
    """Represent a association dict type."""

    node_id: int
    endpoint: Optional[int] = None
