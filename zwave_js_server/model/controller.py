"""Provide a model for the Z-Wave JS controller."""
from typing import TYPE_CHECKING, Dict, List, Optional, TypedDict, cast

from ..event import Event, EventBase
from .association import Association, AssociationGroup
from .node import Node

if TYPE_CHECKING:
    from ..client import Client


class ControllerDataType(TypedDict, total=False):
    """Represent a node data dict type."""

    libraryVersion: str
    type: int
    homeId: int
    ownNodeId: int
    isSecondary: bool  # TODO: The following items are missing in the docs.
    isUsingHomeIdFromOtherNetwork: bool
    isSISPresent: bool
    wasRealPrimary: bool
    isStaticUpdateController: bool
    isSlave: bool
    serialApiVersion: str
    manufacturerId: int
    productType: int
    productId: int
    supportedFunctionTypes: List[int]
    sucNodeId: int
    supportsTimers: bool
    isHealNetworkActive: bool


class Controller(EventBase):
    """Represent a Z-Wave JS controller."""

    def __init__(self, client: "Client", state: dict) -> None:
        """Initialize controller."""
        super().__init__()
        self.client = client
        self.data: ControllerDataType = state["controller"]
        self.nodes: Dict[int, Node] = {}
        for node_state in state["nodes"]:
            node = Node(client, node_state)
            self.nodes[node.node_id] = node

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{type(self).__name__}(home_id={self.home_id})"

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.home_id)

    def __eq__(self, other: object) -> bool:
        """Return whether this instance equals another."""
        if not isinstance(other, Controller):
            return False
        return self.home_id == other.home_id

    @property
    def library_version(self) -> Optional[str]:
        """Return library_version."""
        return self.data.get("libraryVersion")

    @property
    def controller_type(self) -> Optional[int]:
        """Return controller_type."""
        return self.data.get("type")

    @property
    def home_id(self) -> Optional[int]:
        """Return home_id."""
        return self.data.get("homeId")

    @property
    def own_node_id(self) -> Optional[int]:
        """Return own_node_id."""
        return self.data.get("ownNodeId")

    @property
    def is_secondary(self) -> Optional[bool]:
        """Return is_secondary."""
        return self.data.get("isSecondary")  # TODO: This is missing in the docs.

    @property
    def is_using_home_id_from_other_network(self) -> Optional[bool]:
        """Return is_using_home_id_from_other_network."""
        return self.data.get("isUsingHomeIdFromOtherNetwork")

    @property
    def is_SIS_present(self) -> Optional[bool]:  # pylint: disable=invalid-name
        """Return is_SIS_present."""
        return self.data.get("isSISPresent")

    @property
    def was_real_primary(self) -> Optional[bool]:
        """Return was_real_primary."""
        return self.data.get("wasRealPrimary")

    @property
    def is_static_update_controller(self) -> Optional[bool]:
        """Return is_static_update_controller."""
        return self.data.get("isStaticUpdateController")

    @property
    def is_slave(self) -> Optional[bool]:
        """Return is_slave."""
        return self.data.get("isSlave")

    @property
    def serial_api_version(self) -> Optional[str]:
        """Return serial_api_version."""
        return self.data.get("serialApiVersion")

    @property
    def manufacturer_id(self) -> Optional[int]:
        """Return manufacturer_id."""
        return self.data.get("manufacturerId")

    @property
    def product_type(self) -> Optional[int]:
        """Return product_type."""
        return self.data.get("productType")

    @property
    def product_id(self) -> Optional[int]:
        """Return product_id."""
        return self.data.get("productId")

    @property
    def supported_function_types(self) -> List[int]:
        """Return supported_function_types."""
        return self.data.get("supportedFunctionTypes", [])

    @property
    def suc_node_id(self) -> Optional[int]:
        """Return suc_node_id."""
        return self.data.get("sucNodeId")

    @property
    def supports_timers(self) -> Optional[bool]:
        """Return supports_timers."""
        return self.data.get("supportsTimers")

    @property
    def is_heal_network_active(self) -> Optional[bool]:
        """Return is_heal_network_active."""
        return self.data.get("isHealNetworkActive")

    async def async_begin_inclusion(
        self, include_non_secure: Optional[bool] = None
    ) -> bool:
        """Send beginInclusion command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.begin_inclusion",
                "includeNonSecure": include_non_secure,
            }
        )
        return cast(bool, data["success"])

    async def async_stop_inclusion(self) -> bool:
        """Send stopInclusion command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.stop_inclusion"}
        )
        return cast(bool, data["success"])

    async def async_begin_exclusion(self) -> bool:
        """Send beginExclusion command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.begin_exclusion"}
        )
        return cast(bool, data["success"])

    async def async_stop_exclusion(self) -> bool:
        """Send stopExclusion command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.stop_exclusion"}
        )
        return cast(bool, data["success"])

    async def async_remove_failed_node(self, node_id: int) -> None:
        """Send removeFailedNode command to Controller."""
        await self.client.async_send_command(
            {"command": "controller.remove_failed_node", "nodeId": node_id}
        )

    async def async_replace_failed_node(
        self, node_id: int, include_non_secure: Optional[bool] = None
    ) -> bool:
        """Send replaceFailedNode command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.replace_failed_node",
                "nodeId": node_id,
                "includeNonSecure": include_non_secure,
            }
        )
        return cast(bool, data["success"])

    async def async_heal_node(self, node_id: int) -> bool:
        """Send healNode command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.heal_node", "nodeId": node_id}
        )
        return cast(bool, data["success"])

    async def async_begin_healing_network(self) -> bool:
        """Send beginHealingNetwork command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.begin_healing_network"}
        )
        return cast(bool, data["success"])

    async def async_stop_healing_network(self) -> bool:
        """Send stopHealingNetwork command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.stop_healing_network"}
        )
        return cast(bool, data["success"])

    async def async_is_failed_node(self, node_id: int) -> bool:
        """Send isFailedNode command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.is_failed_node", "nodeId": node_id}
        )
        return cast(bool, data["failed"])

    async def async_get_association_groups(
        self, node_id: int
    ) -> Dict[int, AssociationGroup]:
        """Send getAssociationGroups command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_association_groups",
                "nodeId": node_id,
            }
        )
        groups = {}
        for key, group in data["groups"].items():
            groups[key] = AssociationGroup(
                max_nodes=group["maxNodes"],
                is_lifeline=group["isLifeline"],
                multi_channel=group["multiChannel"],
                label=group["label"],
                profile=group.get("profile"),
                issued_commands=group.get("issuedCommands", {}),
            )
        return groups

    async def async_get_associations(self, node_id: int) -> Dict[int, Association]:
        """Send getAssociations command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_associations",
                "nodeId": node_id,
            }
        )
        associations = {}
        for key, association in data["associations"].items():
            associations[key] = Association(
                node_id=association["nodeId"], endpoint=association.get("endpoint")
            )
        return associations

    async def async_is_association_allowed(
        self, node_id: int, group: int, association: Association
    ) -> bool:
        """Send isAssociationAllowed command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.is_association_allowed",
                "nodeId": node_id,
                "group": group,
                "association": {
                    "nodeId": association.node_id,
                    "endpoint": association.endpoint,
                },
            }
        )
        return cast(bool, data["allowed"])

    async def async_add_associations(
        self, node_id: int, group: int, associations: List[Association]
    ) -> None:
        """Send addAssociations command to Controller."""
        await self.client.async_send_command(
            {
                "command": "controller.add_associations",
                "nodeId": node_id,
                "group": group,
                "associations": [
                    {
                        "nodeId": association.node_id,
                        "endpoint": association.endpoint,
                    }
                    for association in associations
                ],
            }
        )

    async def async_remove_associations(
        self, node_id: int, group: int, associations: List[Association]
    ) -> None:
        """Send removeAssociations command to Controller."""
        await self.client.async_send_command(
            {
                "command": "controller.remove_associations",
                "nodeId": node_id,
                "group": group,
                "associations": [
                    {
                        "nodeId": association.node_id,
                        "endpoint": association.endpoint,
                    }
                    for association in associations
                ],
            }
        )

    async def async_remove_node_from_all_associations(self, node_id: int) -> None:
        """Send removeNodeFromAllAssociations command to Controller."""
        await self.client.async_send_command(
            {
                "command": "controller.remove_node_from_all_associations",
                "nodeId": node_id,
            }
        )

    async def async_get_node_neighbors(self, node_id: int) -> List[int]:
        """Send getNodeNeighbors command to Controller to get node's neighbors."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_node_neighbors",
                "nodeId": node_id,
            }
        )
        return cast(List[int], data["neighbors"])

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
        node = event.data["node"] = Node(self.client, event.data["node"])
        self.nodes[node.node_id] = node

    def handle_node_removed(self, event: Event) -> None:
        """Process a node removed event."""
        event.data["node"] = self.nodes.pop(event.data["node"]["nodeId"])

    def handle_heal_network_progress(self, event: Event) -> None:
        """Process a heal network progress event."""
        # pylint: disable=unused-argument
        self.data["isHealNetworkActive"] = True

    def handle_heal_network_done(self, event: Event) -> None:
        """Process a heal network done event."""
        # pylint: disable=unused-argument
        self.data["isHealNetworkActive"] = False
