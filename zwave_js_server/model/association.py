"""Provide a model for the association."""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AssociationGroup:
    """Represent a association group dict type."""

    maxNodes: int  # pylint: disable=invalid-name
    isLifeline: bool  # pylint: disable=invalid-name
    multiChannel: bool  # pylint: disable=invalid-name
    label: str
    profile: Optional[int] = None
    issuedCommands: Optional[  # pylint: disable=invalid-name
        Dict[int, List[int]]
    ] = None


@dataclass
class Association:
    """Represent a association dict type."""

    nodeId: int  # pylint: disable=invalid-name
    endpoint: Optional[int] = None
