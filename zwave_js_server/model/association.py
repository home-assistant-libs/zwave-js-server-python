"""Provide a model for the association."""
from typing import Dict, List, Optional, TypedDict


class AssociationGroupType(TypedDict):
    """Represent a association group dict type."""

    maxNodes: int  # required
    isLifeline: bool  # required
    multiChannel: bool  # required
    label: str  # required
    profile: int
    issuedCommands: Dict[int, List[int]]


class AssociationType(TypedDict):
    """Represent a association dict type."""

    nodeId: int  # required
    endpoint: int


class AssociationGroup:
    """Represent association group."""

    def __init__(self, data: AssociationGroupType) -> None:
        """Initialize group."""
        self.data = data

    @property
    def max_nodes(self) -> int:
        """Return maxNodes."""
        return self.data["maxNodes"]

    @property
    def is_lifeline(self) -> bool:
        """Return isLifeline."""
        return self.data["isLifeline"]

    @property
    def multi_channel(self) -> bool:
        """Return multiChannel."""
        return self.data["multiChannel"]

    @property
    def label(self) -> str:
        """Return label."""
        return self.data["label"]

    @property
    def profile(self) -> Optional[int]:
        """Return profile."""
        return self.data.get("profile")

    @property
    def issued_commands(self) -> Optional[Dict[int, List[int]]]:
        """Return issuedCommands."""
        return self.data.get("issuedCommands")


class Association:
    """Represent association."""

    def __init__(self, data: AssociationType) -> None:
        """Initialize association."""
        self.data = data

    @property
    def node_id(self) -> int:
        """Return nodeId."""
        return self.data["nodeId"]

    @property
    def endpoint(self) -> Optional[int]:
        """Return endpoint."""
        return self.data.get("endpoint")
