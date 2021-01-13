"""Provide a model for the association."""
from typing import Dict, List, Optional, TypedDict
from dataclasses import dataclass


@dataclass
class AssociationGroupType(TypedDict):
    """Represent a association group dict type."""

    maxNodes: int  # pylint: disable=invalid-name
    isLifeline: bool  # pylint: disable=invalid-name
    multiChannel: bool  # pylint: disable=invalid-name
    label: str
    profile: Optional[int]
    issuedCommands: Optional[Dict[int, List[int]]]  # pylint: disable=invalid-name


@dataclass
class AssociationType(TypedDict):
    """Represent a association dict type."""

    nodeId: int  # pylint: disable=invalid-name
    endpoint: Optional[int]
