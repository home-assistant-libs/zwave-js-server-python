"""Provide a model for the Z-Wave JS controller."""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, cast

from zwave_js_server.model.node.firmware import (
    NodeFirmwareUpdateFileInfo,
    NodeFirmwareUpdateInfo,
)

from ...const import (
    MINIMUM_QR_STRING_LENGTH,
    ExclusionStrategy,
    InclusionState,
    InclusionStrategy,
    NodeType,
    QRCodeVersion,
    RFRegion,
    ZwaveFeature,
)
from ...event import Event, EventBase
from ...util.helpers import convert_base64_to_bytes, convert_bytes_to_base64
from ..association import AssociationAddress, AssociationGroup
from ..node import Node
from .data_model import ControllerDataType
from .event_model import CONTROLLER_EVENT_MODEL_MAP
from .firmware import ControllerFirmwareUpdateProgress, ControllerFirmwareUpdateResult
from .inclusion_and_provisioning import (
    InclusionGrant,
    ProvisioningEntry,
    QRProvisioningInformation,
)
from .statistics import ControllerLifelineRoutes, ControllerStatistics

if TYPE_CHECKING:
    from ...client import Client


@dataclass
class NVMProgress:
    """Class to represent an NVM backup/restore progress event."""

    bytes_read_or_written: int
    total_bytes: int


class Controller(EventBase):
    """Represent a Z-Wave JS controller."""

    def __init__(self, client: "Client", state: dict) -> None:
        """Initialize controller."""
        super().__init__()
        self.client = client
        self.nodes: Dict[int, Node] = {}
        self._heal_network_progress: Optional[Dict[int, str]] = None
        self._statistics = ControllerStatistics()
        for node_state in state["nodes"]:
            node = Node(client, node_state)
            self.nodes[node.node_id] = node
        self.update(state["controller"])

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
    def sdk_version(self) -> Optional[str]:
        """Return sdk_version."""
        return self.data.get("sdkVersion")

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
    def own_node(self) -> Optional[Node]:
        """Return own_node."""
        if self.own_node_id is None:
            return None
        return self.nodes.get(self.own_node_id)

    @property
    def is_primary(self) -> Optional[bool]:
        """Return is_primary."""
        return self.data.get("isPrimary")

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
    def is_suc(self) -> Optional[bool]:
        """Return is_suc."""
        return self.data.get("isSUC")

    @property
    def node_type(self) -> Optional[NodeType]:
        """Return node_type."""
        if (node_type := self.data.get("nodeType")) is not None:
            return NodeType(node_type)
        return None

    @property
    def firmware_version(self) -> Optional[str]:
        """Return firmware_version."""
        return self.data.get("firmwareVersion")

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

    @property
    def statistics(self) -> ControllerStatistics:
        """Return statistics property."""
        return self._statistics

    @property
    def heal_network_progress(self) -> Optional[Dict[int, str]]:
        """Return heal network progress state."""
        return self._heal_network_progress

    @property
    def inclusion_state(self) -> InclusionState:
        """Return inclusion state."""
        return InclusionState(self.data["inclusionState"])

    @property
    def rf_region(self) -> Optional[RFRegion]:
        """Return RF region of controller."""
        if (rf_region := self.data.get("rfRegion")) is None:
            return None
        return RFRegion(rf_region)

    def update(self, data: ControllerDataType) -> None:
        """Update controller data."""
        self.data = data
        self._statistics = ControllerStatistics(self.data.get("statistics"))

    async def async_begin_inclusion(
        self,
        inclusion_strategy: Literal[
            InclusionStrategy.DEFAULT,
            InclusionStrategy.SECURITY_S0,
            InclusionStrategy.SECURITY_S2,
            InclusionStrategy.INSECURE,
        ],
        force_security: Optional[bool] = None,
        provisioning: Optional[
            Union[str, ProvisioningEntry, QRProvisioningInformation]
        ] = None,
    ) -> bool:
        """Send beginInclusion command to Controller."""
        # Most functionality was introduced in Schema 8
        require_schema = 8
        options: Dict[str, Any] = {"strategy": inclusion_strategy}
        # forceSecurity can only be used with the default inclusion strategy
        if force_security is not None:
            if inclusion_strategy != InclusionStrategy.DEFAULT:
                raise ValueError(
                    "`forceSecurity` option is only supported with inclusion_strategy=DEFAULT"
                )
            options["forceSecurity"] = force_security

        # provisioning can only be used with the S2 inclusion strategy and may need
        # additional processing
        if provisioning is not None:
            if inclusion_strategy != InclusionStrategy.SECURITY_S2:
                raise ValueError(
                    "`provisioning` option is only supported with inclusion_strategy=SECURITY_S2"
                )
            # Provisioning option was introduced in Schema 11
            require_schema = 11
            # String is assumed to be the QR code string so we can pass as is
            if isinstance(provisioning, str):
                if len(
                    provisioning
                ) < MINIMUM_QR_STRING_LENGTH or not provisioning.startswith("90"):
                    raise ValueError(
                        f"QR code string must be at least {MINIMUM_QR_STRING_LENGTH} characters "
                        "long and start with `90`"
                    )
                options["provisioning"] = provisioning
            # If we get a Smart Start QR code, we provision the node and return because
            # inclusion is over
            elif (
                isinstance(provisioning, QRProvisioningInformation)
                and provisioning.version == QRCodeVersion.SMART_START
            ):
                raise ValueError(
                    "Smart Start QR codes can't use the normal inclusion process. Use the "
                    "provision_smart_start_node command to provision this device."
                )
            # Otherwise we assume the data is ProvisioningEntry or
            # QRProvisioningInformation that is not a Smart Start QR code
            else:
                options["provisioning"] = provisioning.to_dict()

        data = await self.client.async_send_command(
            {
                "command": "controller.begin_inclusion",
                "options": options,
            },
            require_schema=require_schema,
        )
        return cast(bool, data["success"])

    async def async_provision_smart_start_node(
        self,
        provisioning_info: Union[ProvisioningEntry, QRProvisioningInformation, str],
    ) -> None:
        """Send provisionSmartStartNode command to Controller."""
        if (
            isinstance(provisioning_info, QRProvisioningInformation)
            and provisioning_info.version == QRCodeVersion.S2
        ):
            raise ValueError(
                "An S2 QR Code can't be used to pre-provision a Smart Start node"
            )
        await self.client.async_send_command(
            {
                "command": "controller.provision_smart_start_node",
                "entry": provisioning_info
                if isinstance(provisioning_info, str)
                else provisioning_info.to_dict(),
            },
            require_schema=11,
        )

    async def async_unprovision_smart_start_node(
        self,
        dsk_or_node_id: Union[str, int],
    ) -> None:
        """Send unprovisionSmartStartNode command to Controller."""
        await self.client.async_send_command(
            {
                "command": "controller.unprovision_smart_start_node",
                "dskOrNodeId": dsk_or_node_id,
            },
            require_schema=11,
        )

    async def async_get_provisioning_entry(
        self, dsk_or_node_id: Union[str, int]
    ) -> Optional[ProvisioningEntry]:
        """Send getProvisioningEntry command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_provisioning_entry",
                "dskOrNodeId": dsk_or_node_id,
            },
            require_schema=17,
        )
        if "entry" in data:
            return ProvisioningEntry.from_dict(data["entry"])
        return None

    async def async_get_provisioning_entries(self) -> List[ProvisioningEntry]:
        """Send getProvisioningEntries command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_provisioning_entries",
            },
            require_schema=11,
        )
        return [ProvisioningEntry.from_dict(entry) for entry in data.get("entries", [])]

    async def async_stop_inclusion(self) -> bool:
        """Send stopInclusion command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.stop_inclusion"}
        )
        return cast(bool, data["success"])

    async def async_begin_exclusion(
        self, strategy: Optional[ExclusionStrategy] = None
    ) -> bool:
        """Send beginExclusion command to Controller."""
        payload: Dict[str, Union[str, ExclusionStrategy]] = {
            "command": "controller.begin_exclusion"
        }
        if strategy is not None:
            payload["strategy"] = strategy
        data = await self.client.async_send_command(payload, require_schema=22)
        return cast(bool, data["success"])

    async def async_stop_exclusion(self) -> bool:
        """Send stopExclusion command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.stop_exclusion"}
        )
        return cast(bool, data["success"])

    async def async_remove_failed_node(self, node: Node) -> None:
        """Send removeFailedNode command to Controller."""
        await self.client.async_send_command(
            {"command": "controller.remove_failed_node", "nodeId": node.node_id}
        )

    async def async_replace_failed_node(
        self,
        node: Node,
        inclusion_strategy: Literal[
            InclusionStrategy.DEFAULT,
            InclusionStrategy.SECURITY_S0,
            InclusionStrategy.SECURITY_S2,
            InclusionStrategy.INSECURE,
        ],
        force_security: Optional[bool] = None,
        provisioning: Optional[
            Union[str, ProvisioningEntry, QRProvisioningInformation]
        ] = None,
    ) -> bool:
        """Send replaceFailedNode command to Controller."""
        # Most functionality was introduced in Schema 8
        require_schema = 8
        options: Dict[str, Any] = {"strategy": inclusion_strategy}
        # forceSecurity can only be used with the default inclusion strategy
        if force_security is not None:
            if inclusion_strategy != InclusionStrategy.DEFAULT:
                raise ValueError(
                    "`forceSecurity` option is only supported with inclusion_strategy=DEFAULT"
                )
            options["forceSecurity"] = force_security

        # provisioning can only be used with the S2 inclusion strategy and may need
        # additional processing
        if provisioning is not None:
            if inclusion_strategy != InclusionStrategy.SECURITY_S2:
                raise ValueError(
                    "`provisioning` option is only supported with inclusion_strategy=SECURITY_S2"
                )
            # Provisioning option was introduced in Schema 11
            require_schema = 11
            # String is assumed to be the QR code string so we can pass as is
            if isinstance(provisioning, str):
                if len(
                    provisioning
                ) < MINIMUM_QR_STRING_LENGTH or not provisioning.startswith("90"):
                    raise ValueError(
                        f"QR code string must be at least {MINIMUM_QR_STRING_LENGTH} characters "
                        "long and start with `90`"
                    )
                options["provisioning"] = provisioning
            # Otherwise we assume the data is ProvisioningEntry or
            # QRProvisioningInformation
            else:
                options["provisioning"] = provisioning.to_dict()

        data = await self.client.async_send_command(
            {
                "command": "controller.replace_failed_node",
                "nodeId": node.node_id,
                "options": options,
            },
            require_schema=require_schema,
        )
        return cast(bool, data["success"])

    async def async_heal_node(self, node: Node) -> bool:
        """Send healNode command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.heal_node", "nodeId": node.node_id}
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
        success = cast(bool, data["success"])
        if success:
            self._heal_network_progress = None
            self.data["isHealNetworkActive"] = False
        return success

    async def async_is_failed_node(self, node: Node) -> bool:
        """Send isFailedNode command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.is_failed_node", "nodeId": node.node_id}
        )
        return cast(bool, data["failed"])

    async def async_get_association_groups(
        self, source: AssociationAddress
    ) -> Dict[int, AssociationGroup]:
        """Send getAssociationGroups command to Controller."""
        source_data = {"nodeId": source.node_id}
        if source.endpoint is not None:
            source_data["endpoint"] = source.endpoint
        data = await self.client.async_send_command(
            {
                "command": "controller.get_association_groups",
                **source_data,
            }
        )
        groups = {}
        for key, group in data["groups"].items():
            groups[int(key)] = AssociationGroup(
                max_nodes=group["maxNodes"],
                is_lifeline=group["isLifeline"],
                multi_channel=group["multiChannel"],
                label=group["label"],
                profile=group.get("profile"),
                issued_commands=group.get("issuedCommands", {}),
            )
        return groups

    async def async_get_associations(
        self, source: AssociationAddress
    ) -> Dict[int, List[AssociationAddress]]:
        """Send getAssociations command to Controller."""
        source_data = {"nodeId": source.node_id}
        if source.endpoint is not None:
            source_data["endpoint"] = source.endpoint
        data = await self.client.async_send_command(
            {
                "command": "controller.get_associations",
                **source_data,
            }
        )
        associations = {}
        for key, association_addresses in data["associations"].items():
            associations[int(key)] = [
                AssociationAddress(
                    node_id=association_address["nodeId"],
                    endpoint=association_address.get("endpoint"),
                )
                for association_address in association_addresses
            ]
        return associations

    async def async_is_association_allowed(
        self, source: AssociationAddress, group: int, association: AssociationAddress
    ) -> bool:
        """Send isAssociationAllowed command to Controller."""
        source_data = {"nodeId": source.node_id}
        if source.endpoint is not None:
            source_data["endpoint"] = source.endpoint

        association_data = {"nodeId": association.node_id}
        if association.endpoint is not None:
            association_data["endpoint"] = association.endpoint
        data = await self.client.async_send_command(
            {
                "command": "controller.is_association_allowed",
                **source_data,
                "group": group,
                "association": association_data,
            }
        )
        return cast(bool, data["allowed"])

    async def async_add_associations(
        self,
        source: AssociationAddress,
        group: int,
        associations: List[AssociationAddress],
        wait_for_result: bool = False,
    ) -> None:
        """Send addAssociations command to Controller."""
        source_data = {"nodeId": source.node_id}
        if source.endpoint is not None:
            source_data["endpoint"] = source.endpoint

        associations_data = []
        for association in associations:
            association_data = {"nodeId": association.node_id}
            if association.endpoint is not None:
                association_data["endpoint"] = association.endpoint
            associations_data.append(association_data)

        cmd = {
            "command": "controller.add_associations",
            **source_data,
            "group": group,
            "associations": associations_data,
        }
        if wait_for_result:
            await self.client.async_send_command(cmd)
        else:
            await self.client.async_send_command_no_wait(cmd)

    async def async_remove_associations(
        self,
        source: AssociationAddress,
        group: int,
        associations: List[AssociationAddress],
        wait_for_result: bool = False,
    ) -> None:
        """Send removeAssociations command to Controller."""
        source_data = {"nodeId": source.node_id}
        if source.endpoint is not None:
            source_data["endpoint"] = source.endpoint

        associations_data = []
        for association in associations:
            association_data = {"nodeId": association.node_id}
            if association.endpoint is not None:
                association_data["endpoint"] = association.endpoint
            associations_data.append(association_data)

        cmd = {
            "command": "controller.remove_associations",
            **source_data,
            "group": group,
            "associations": associations_data,
        }
        if wait_for_result:
            await self.client.async_send_command(cmd)
        else:
            await self.client.async_send_command_no_wait(cmd)

    async def async_remove_node_from_all_associations(
        self,
        node: Node,
        wait_for_result: bool = False,
    ) -> None:
        """Send removeNodeFromAllAssociations command to Controller."""
        cmd = {
            "command": "controller.remove_node_from_all_associations",
            "nodeId": node.node_id,
        }
        if wait_for_result:
            await self.client.async_send_command(cmd)
        else:
            await self.client.async_send_command_no_wait(cmd)

    async def async_get_node_neighbors(self, node: Node) -> List[int]:
        """Send getNodeNeighbors command to Controller to get node's neighbors."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_node_neighbors",
                "nodeId": node.node_id,
            }
        )
        return cast(List[int], data["neighbors"])

    async def async_grant_security_classes(
        self, inclusion_grant: InclusionGrant
    ) -> None:
        """Send grantSecurityClasses command to Controller."""
        await self.client.async_send_command(
            {
                "command": "controller.grant_security_classes",
                "inclusionGrant": inclusion_grant.to_dict(),
            }
        )

    async def async_validate_dsk_and_enter_pin(self, pin: str) -> None:
        """Send validateDSKAndEnterPIN command to Controller."""
        await self.client.async_send_command(
            {
                "command": "controller.validate_dsk_and_enter_pin",
                "pin": pin,
            }
        )

    async def async_supports_feature(self, feature: ZwaveFeature) -> Optional[bool]:
        """
        Send supportsFeature command to Controller.

        When None is returned it means the driver does not yet know whether the
        controller supports the input feature.
        """
        data = await self.client.async_send_command(
            {"command": "controller.supports_feature", "feature": feature.value},
            require_schema=12,
        )
        return cast(Optional[bool], data.get("supported"))

    async def async_get_state(self) -> ControllerDataType:
        """Get controller state."""
        data = await self.client.async_send_command(
            {"command": "controller.get_state"}, require_schema=14
        )
        return cast(ControllerDataType, data["state"])

    async def async_backup_nvm_raw(self) -> bytes:
        """Send backupNVMRaw command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.backup_nvm_raw"}, require_schema=14
        )
        return convert_base64_to_bytes(data["nvmData"])

    async def async_restore_nvm(self, file: bytes) -> None:
        """Send restoreNVM command to Controller."""
        await self.client.async_send_command(
            {
                "command": "controller.restore_nvm",
                "nvmData": convert_bytes_to_base64(file),
            },
            require_schema=14,
        )

    async def async_get_power_level(self) -> Dict[str, int]:
        """Send getPowerlevel command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.get_powerlevel"}, require_schema=14
        )
        return {
            "power_level": data["powerlevel"],
            "measured_0_dbm": data["measured0dBm"],
        }

    async def async_set_power_level(
        self, power_level: int, measured_0_dbm: int
    ) -> bool:
        """Send setPowerlevel command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.set_powerlevel",
                "powerlevel": power_level,
                "measured0dBm": measured_0_dbm,
            },
            require_schema=14,
        )
        return cast(bool, data["success"])

    async def async_get_rf_region(self) -> RFRegion:
        """Send getRFRegion command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.get_rf_region"}, require_schema=14
        )
        return RFRegion(data["region"])

    async def async_set_rf_region(self, rf_region: RFRegion) -> bool:
        """Send setRFRegion command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.set_rf_region",
                "region": rf_region.value,
            },
            require_schema=14,
        )
        return cast(bool, data["success"])

    async def async_get_known_lifeline_routes(
        self,
    ) -> Dict[Node, ControllerLifelineRoutes]:
        """Send getKnownLifelineRoutes command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.get_known_lifeline_routes"}, require_schema=16
        )

        return {
            self.nodes[node_id]: ControllerLifelineRoutes(self.client, lifeline_routes)
            for node_id, lifeline_routes in data["routes"].items()
        }

    async def async_is_any_ota_firmware_update_in_progress(self) -> bool:
        """
        Send isAnyOTAFirmwareUpdateInProgress command to Controller.

        If `True`, a firmware update is in progress on at least one node.
        """
        data = await self.client.async_send_command(
            {"command": "controller.is_any_ota_firmware_update_in_progress"},
            require_schema=21,
        )
        assert data
        return cast(bool, data["progress"])

    async def async_get_available_firmware_updates(
        self, node: Node, api_key: str, include_prereleases: bool = False
    ) -> List[NodeFirmwareUpdateInfo]:
        """Send getAvailableFirmwareUpdates command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_available_firmware_updates",
                "nodeId": node.node_id,
                "apiKey": api_key,
                "includePrereleases": include_prereleases,
            },
            require_schema=24,
        )
        assert data
        return [NodeFirmwareUpdateInfo.from_dict(update) for update in data["updates"]]

    async def async_firmware_update_ota(
        self, node: Node, updates: List[NodeFirmwareUpdateFileInfo]
    ) -> bool:
        """Send firmwareUpdateOTA command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.firmware_update_ota",
                "nodeId": node.node_id,
                "updates": [update.to_dict() for update in updates],
            },
            require_schema=24,
        )
        return cast(bool, data["success"])

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

        CONTROLLER_EVENT_MODEL_MAP[event.type](**event.data)

        self._handle_event_protocol(event)

        event.data["controller"] = self
        self.emit(event.type, event.data)

    def handle_firmware_update_progress(self, event: Event) -> None:
        """Process a firmware update progress event."""
        event.data["firmware_update_progress"] = ControllerFirmwareUpdateProgress(
            event.data["progress"]
        )

    def handle_firmware_update_finished(self, event: Event) -> None:
        """Process a firmware update finished event."""
        event.data["firmware_update_finished"] = ControllerFirmwareUpdateResult(
            event.data["result"]
        )

    def handle_inclusion_failed(self, event: Event) -> None:
        """Process an inclusion failed event."""

    def handle_exclusion_failed(self, event: Event) -> None:
        """Process an exclusion failed event."""

    def handle_inclusion_started(self, event: Event) -> None:
        """Process an inclusion started event."""

    def handle_exclusion_started(self, event: Event) -> None:
        """Process an exclusion started event."""

    def handle_inclusion_stopped(self, event: Event) -> None:
        """Process an inclusion stopped event."""

    def handle_exclusion_stopped(self, event: Event) -> None:
        """Process an exclusion stopped event."""

    def handle_node_found(self, event: Event) -> None:
        """Process a node found event."""

    def handle_node_added(self, event: Event) -> None:
        """Process a node added event."""
        node = event.data["node"] = Node(self.client, event.data["node"])
        self.nodes[node.node_id] = node

    def handle_node_removed(self, event: Event) -> None:
        """Process a node removed event."""
        event.data["node"] = self.nodes.pop(event.data["node"]["nodeId"])
        # Remove client from node since it's no longer connected to the controller
        event.data["node"].client = None

    def handle_heal_network_progress(self, event: Event) -> None:
        """Process a heal network progress event."""
        self._heal_network_progress = event.data["progress"].copy()
        self.data["isHealNetworkActive"] = True

    def handle_heal_network_done(self, event: Event) -> None:
        """Process a heal network done event."""
        # pylint: disable=unused-argument
        self._heal_network_progress = None
        self.data["isHealNetworkActive"] = False

    def handle_statistics_updated(self, event: Event) -> None:
        """Process a statistics updated event."""
        self.data["statistics"] = statistics = event.data["statistics"]
        self._statistics = event.data["statistics_updated"] = ControllerStatistics(
            statistics
        )

    def handle_grant_security_classes(self, event: Event) -> None:
        """Process a grant security classes event."""
        event.data["requested_grant"] = InclusionGrant.from_dict(
            event.data["requested"]
        )

    def handle_validate_dsk_and_enter_pin(self, event: Event) -> None:
        """Process a validate dsk and enter pin event."""

    def handle_inclusion_aborted(self, event: Event) -> None:
        """Process an inclusion aborted event."""

    def handle_nvm_backup_progress(self, event: Event) -> None:
        """Process a nvm backup progress event."""
        event.data["nvm_backup_progress"] = NVMProgress(
            event.data["bytesRead"], event.data["total"]
        )

    def handle_nvm_convert_progress(self, event: Event) -> None:
        """Process a nvm convert progress event."""
        event.data["nvm_convert_progress"] = NVMProgress(
            event.data["bytesRead"], event.data["total"]
        )

    def handle_nvm_restore_progress(self, event: Event) -> None:
        """Process a nvm restore progress event."""
        event.data["nvm_restore_progress"] = NVMProgress(
            event.data["bytesWritten"], event.data["total"]
        )
