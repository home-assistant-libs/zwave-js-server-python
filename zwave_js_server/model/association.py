"""Provide a model for the association."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .controller import Controller
    from .node import Node


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

    controller: Controller
    node_id: int
    endpoint: int | None = None

    @property
    def node(self) -> Node | None:
        """Return the node."""
        if self.node_id in self.controller.nodes:
            return self.controller.nodes[self.node_id]
        return None
