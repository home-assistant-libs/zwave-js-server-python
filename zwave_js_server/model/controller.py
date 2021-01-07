"""Provide a model for the Z-Wave JS controller."""
from typing import Dict, List

from ..event import Event, EventBase
from .node import Node


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

    def receive_event(self, event: Event) -> None:
        """Receive an event."""
        if event.data["source"] == "node":
            node = self.nodes.get(event.data["nodeId"])
            if node is None:
                # TODO handle event for unknown node
                pass
            else:
                node.receive_event(event)
            return

        if event.data["source"] != "controller":
            # TODO decide what to do here
            print(
                f"Controller doesn't know how to handle/forward this event: {event.data}"
            )

        self._handle_event_protocol(event)

        event.data["controller"] = self
        self.emit(event.type, event.data)

    def handle_inclusion_failed(self, event: Event) -> None:
        """Process an inclusion failed event."""

    def handle_exclusion_failed(self, event: Event) -> None:
        """Process an exclusion failed event."""

    def handle_inclusion_started(self, event: Event) -> None:
        """Process an inclusion started event."""

    def handle_exclusion_started(self, event: Event) -> None:
        """Process an exclustion started event."""

    def handle_inclusion_stopped(self, event: Event) -> None:
        """Process an inclusion stopped event."""

    def handle_exclusion_stopped(self, event: Event) -> None:
        """Process an exclusion stopped event."""

    def handle_node_added(self, event: Event) -> None:
        """Process a node added event."""
        node = event.data["node"] = Node(event.data["node"])
        self.nodes[node.node_id] = node

    def handle_node_removed(self, event: Event) -> None:
        """Process a node removed event."""
        event.data["node"] = self.nodes.pop(event.data["node"]["nodeId"])

    def handle_heal_network_progress(self, event: Event) -> None:
        """Process a heal network progress event."""

    def handle_heal_network_done(self, event: Event) -> None:
        """Process a heal network done event."""
