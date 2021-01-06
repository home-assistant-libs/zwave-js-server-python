"""Provide a model for the gateway."""
from dataclasses import dataclass, field
from typing import Dict

from ..protocol import gateway as protocol, get_handler
from .controller import Controller
from .node import Node


@dataclass
class GatewayEvent:
    """Represent a gateway event."""

    type: str
    data: dict = field(default_factory=dict)


class Gateway:
    """Represent a Z-Wave gateway."""

    def __init__(self, state: dict):
        """Set up gateway."""
        self.nodes: Dict[int, Node] = {}
        self.controller = Controller.from_state(state["controller"])
        for node_state in state["nodes"]:
            node = Node.from_state(node_state)
            self.nodes[node.node_id] = node

    def handle_event(self, event: GatewayEvent) -> None:
        """Handle a zwave-js event."""
        event_handler = get_handler(protocol, event)
        event_handler(self, event)
