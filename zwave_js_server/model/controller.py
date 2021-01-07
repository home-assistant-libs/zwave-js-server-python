"""Provide a model for the Z-Wave JS controller."""
from dataclasses import dataclass, field
from typing import Dict, List, cast

from ..event import EventBase
from ..protocol import ProtocolType, controller as protocol, get_handler
from .node import Node, NodeEvent


@dataclass
class ControllerEvent:
    """Represent a Controller event."""

    type: str
    data: dict = field(default_factory=dict)


class Controller(EventBase):
    """Represent a Z-Wave JS controller."""

    def __init__(self, state: dict) -> None:
        """Initialize controller."""
        super().__init__()
        self.data = state["controller"]
        self.nodes: Dict[int, Node] = {}
        for node_state in state["nodes"]:
            node = Node(node_state)
            self.nodes[node.node_id] = node

    @property
    def library_version(self) -> str:
        """Return library_version."""
        return self.data.get("libraryVersion")

    @property
    def controller_type(self) -> int:
        """Return controller_type."""
        return self.data.get("type")

    @property
    def home_id(self) -> int:
        """Return home_id."""
        return self.data.get("homeId")

    @property
    def own_node_id(self) -> int:
        """Return own_node_id."""
        return self.data.get("ownNodeId")

    @property
    def is_secondary(self) -> bool:
        """Return is_secondary."""
        return self.data.get("isSecondary")

    @property
    def is_using_home_id_from_other_network(self) -> bool:
        """Return is_using_home_id_from_other_network."""
        return self.data.get("isUsingHomeIdFromOtherNetwork")

    @property
    def is_SIS_present(self) -> bool:  # pylint: disable=invalid-name
        """Return is_SIS_present."""
        return self.data.get("isSISPresent")

    @property
    def was_real_primary(self) -> bool:
        """Return was_real_primary."""
        return self.data.get("wasRealPrimary")

    @property
    def is_static_update_controller(self) -> bool:
        """Return is_static_update_controller."""
        return self.data.get("isStaticUpdateController")

    @property
    def is_slave(self) -> bool:
        """Return is_slave."""
        return self.data.get("isSlave")

    @property
    def serial_api_version(self) -> str:
        """Return serial_api_version."""
        return self.data.get("serialApiVersion")

    @property
    def manufacturer_id(self) -> int:
        """Return manufacturer_id."""
        return self.data.get("manufacturerId")

    @property
    def product_type(self) -> int:
        """Return product_type."""
        return self.data.get("productType")

    @property
    def product_id(self) -> int:
        """Return product_id."""
        return self.data.get("productId")

    @property
    def supported_function_types(self) -> List[int]:
        """Return supported_function_types."""
        return self.data.get("supportedFunctionTypes")

    @property
    def suc_node_id(self) -> int:
        """Return suc_node_id."""
        return self.data.get("sucNodeId")

    @property
    def supports_timers(self) -> bool:
        """Return supports_timers."""
        return self.data.get("supportsTimers")

    def handle_event(self, event: ControllerEvent) -> None:
        """Receive an event."""
        if event.data["source"] == "node":
            node = self.nodes.get(event.data["nodeId"])
            if node is None:
                # TODO handle event for unknown node
                pass
            else:
                node_event = NodeEvent(type=event.data["event"], data=event.data)
                # FIXME: Complete node protocol.
                node.handle_event(node_event.data)
            return

        if event.data["source"] != "controller":
            # TODO decide what to do here
            print(
                f"Controller doesn't know how to handle/forward this event: {event.data}"
            )

        protocol_ = cast(ProtocolType, protocol)
        event_handler = get_handler(protocol_, event)
        event_handler(self, event)

        event.data["controller"] = self
        self.emit(event.data["event"], event.data)
