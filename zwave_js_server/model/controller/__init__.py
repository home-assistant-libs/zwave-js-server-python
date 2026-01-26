"""Provide a model for the Z-Wave JS controller."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Any, Literal, cast

from zwave_js_server.model.node.firmware import NodeFirmwareUpdateInfo

from ...const import (
    MINIMUM_QR_STRING_LENGTH,
    AssociationCheckResult,
    ControllerStatus,
    ExclusionStrategy,
    InclusionState,
    InclusionStrategy,
    NodeType,
    QRCodeVersion,
    RFRegion,
    RemoveNodeReason,
    ZwaveFeature,
)
from ...event import Event, EventBase
from ...util.helpers import convert_base64_to_bytes, convert_bytes_to_base64
from ..association import AssociationAddress, AssociationGroup
from ..node import Node
from ..node.firmware import NodeFirmwareUpdateResult
from .data_model import (
    ControllerDataType,
    ZWaveApiVersionDataType,
    ZWaveChipTypeDataType,
)
from .event_model import CONTROLLER_EVENT_MODEL_MAP
from .inclusion_and_provisioning import (
    InclusionGrant,
    ProvisioningEntry,
    QRProvisioningInformation,
)
from .rebuild_routes import (
    RebuildRoutesOptions,
    RebuildRoutesOptionsDataType,
    RebuildRoutesStatus,
)
from .statistics import (
    ControllerLifelineRoutes,
    ControllerStatistics,
    ControllerStatisticsDataType,
)

if TYPE_CHECKING:
    from ...client import Client

_LOGGER = logging.getLogger(__package__)

DEFAULT_CONTROLLER_STATISTICS = (  # pylint: disable=invalid-name
    ControllerStatisticsDataType(
        messagesTX=0,
        messagesRX=0,
        messagesDroppedTX=0,
        messagesDroppedRX=0,
        NAK=0,
        CAN=0,
        timeoutACK=0,
        timeoutResponse=0,
        timeoutCallback=0,
    )
)


@dataclass
class NVMProgress:
    """Class to represent an NVM backup/restore progress event."""

    bytes_read_or_written: int
    total_bytes: int


class Controller(EventBase):
    """Represent a Z-Wave JS controller."""

    def __init__(self, client: Client, state: dict) -> None:
        """Initialize controller."""
        super().__init__()
        self.client = client
        self.nodes: dict[int, Node] = {}
        self._rebuild_routes_progress: dict[Node, RebuildRoutesStatus] | None = None
        self._last_rebuild_routes_result: dict[Node, RebuildRoutesStatus] | None = None
        self._statistics = ControllerStatistics(DEFAULT_CONTROLLER_STATISTICS)
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

    def _generate_rebuild_routes_status(
        self, data: dict[str, str]
    ) -> dict[Node, RebuildRoutesStatus]:
        """Generate rebuild routes status."""
        return {
            self.nodes[int(node_id)]: RebuildRoutesStatus(status)
            for node_id, status in data.items()
        }

    @property
    def sdk_version(self) -> str | None:
        """Return sdk_version."""
        return self.data.get("sdkVersion")

    @property
    def controller_type(self) -> int | None:
        """Return controller_type."""
        return self.data.get("type")

    @property
    def home_id(self) -> int | None:
        """Return home_id."""
        return self.data.get("homeId")

    @property
    def own_node_id(self) -> int | None:
        """Return own_node_id."""
        return self.data.get("ownNodeId")

    @property
    def own_node(self) -> Node | None:
        """Return own_node."""
        if self.own_node_id is None:
            return None
        return self.nodes.get(self.own_node_id)

    @property
    def is_primary(self) -> bool | None:
        """Return is_primary."""
        return self.data.get("isPrimary")

    @property
    def is_using_home_id_from_other_network(self) -> bool | None:
        """Return is_using_home_id_from_other_network."""
        return self.data.get("isUsingHomeIdFromOtherNetwork")

    @property
    def is_SIS_present(self) -> bool | None:  # pylint: disable=invalid-name
        """Return is_SIS_present."""
        return self.data.get("isSISPresent")

    @property
    def was_real_primary(self) -> bool | None:
        """Return was_real_primary."""
        return self.data.get("wasRealPrimary")

    @property
    def is_suc(self) -> bool | None:
        """Return is_suc."""
        return self.data.get("isSUC")

    @property
    def node_type(self) -> NodeType | None:
        """Return node_type."""
        if (node_type := self.data.get("nodeType")) is not None:
            return NodeType(node_type)
        return None

    @property
    def firmware_version(self) -> str | None:
        """Return firmware_version."""
        return self.data.get("firmwareVersion")

    @property
    def manufacturer_id(self) -> int | None:
        """Return manufacturer_id."""
        return self.data.get("manufacturerId")

    @property
    def product_type(self) -> int | None:
        """Return product_type."""
        return self.data.get("productType")

    @property
    def product_id(self) -> int | None:
        """Return product_id."""
        return self.data.get("productId")

    @property
    def supported_function_types(self) -> list[int]:
        """Return supported_function_types."""
        return self.data.get("supportedFunctionTypes", [])

    @property
    def suc_node_id(self) -> int | None:
        """Return suc_node_id."""
        return self.data.get("sucNodeId")

    @property
    def supports_timers(self) -> bool | None:
        """Return supports_timers."""
        return self.data.get("supportsTimers")

    @property
    def is_rebuilding_routes(self) -> bool | None:
        """Return is_rebuilding_routes."""
        return self.data.get("isRebuildingRoutes")

    @property
    def statistics(self) -> ControllerStatistics:
        """Return statistics property."""
        return self._statistics

    @property
    def rebuild_routes_progress(self) -> dict[Node, RebuildRoutesStatus] | None:
        """Return rebuild routes progress state."""
        return self._rebuild_routes_progress

    @property
    def last_rebuild_routes_result(self) -> dict[Node, RebuildRoutesStatus] | None:
        """Return the last rebuild routes result."""
        return self._last_rebuild_routes_result

    @property
    def inclusion_state(self) -> InclusionState:
        """Return inclusion state."""
        return InclusionState(self.data["inclusionState"])

    @property
    def rf_region(self) -> RFRegion | None:
        """Return RF region of controller."""
        if (rf_region := self.data.get("rfRegion")) is None:
            return None
        return RFRegion(rf_region)

    @property
    def status(self) -> ControllerStatus:
        """Return status."""
        return ControllerStatus(self.data["status"])

    @property
    def supports_long_range(self) -> bool | None:
        """Return whether controller supports long range or not."""
        return self.data.get("supportsLongRange")

    # Schema 45+ properties

    @property
    def is_sis(self) -> bool | None:
        """Return whether this controller is the SIS (Static Information Station)."""
        return self.data.get("isSIS")

    @property
    def max_payload_size(self) -> int | None:
        """Return maximum Z-Wave payload size."""
        return self.data.get("maxPayloadSize")

    @property
    def max_payload_size_lr(self) -> int | None:
        """Return maximum Long Range payload size."""
        return self.data.get("maxPayloadSizeLR")

    @property
    def zwave_api_version(self) -> ZWaveApiVersionDataType | None:
        """Return Z-Wave API version info (kind, version)."""
        return self.data.get("zwaveApiVersion")

    @property
    def zwave_chip_type(self) -> ZWaveChipTypeDataType | None:
        """Return controller chip type info."""
        return self.data.get("zwaveChipType")

    def update(self, data: ControllerDataType) -> None:
        """Update controller data."""
        self.data = data
        self._statistics = ControllerStatistics(
            self.data.get("statistics", DEFAULT_CONTROLLER_STATISTICS)
        )
        if "rebuildRoutesProgress" in self.data:
            self._rebuild_routes_progress = self._generate_rebuild_routes_status(
                self.data["rebuildRoutesProgress"]
            )

    async def async_begin_inclusion(
        self,
        inclusion_strategy: Literal[
            InclusionStrategy.DEFAULT,
            InclusionStrategy.SECURITY_S0,
            InclusionStrategy.SECURITY_S2,
            InclusionStrategy.INSECURE,
        ],
        force_security: bool | None = None,
        provisioning: str | ProvisioningEntry | QRProvisioningInformation | None = None,
        dsk: str | None = None,
    ) -> bool:
        """Send beginInclusion command to Controller."""
        # Most functionality was introduced in Schema 8
        require_schema = 8
        options: dict[str, Any] = {"strategy": inclusion_strategy}
        # forceSecurity can only be used with the default inclusion strategy
        if force_security is not None:
            if inclusion_strategy != InclusionStrategy.DEFAULT:
                raise ValueError(
                    "`forceSecurity` option is only supported with inclusion_strategy="
                    "DEFAULT"
                )
            options["forceSecurity"] = force_security

        # provisioning can only be used with the S2 inclusion strategy and may need
        # additional processing
        if provisioning is not None:
            if inclusion_strategy != InclusionStrategy.SECURITY_S2:
                raise ValueError(
                    "`provisioning` option is only supported with inclusion_strategy="
                    "SECURITY_S2"
                )

            if dsk is not None:
                raise ValueError("Only one of `provisioning` and `dsk` can be provided")
            # Provisioning option was introduced in Schema 11
            require_schema = 11
            # String is assumed to be the QR code string so we can pass as is
            if isinstance(provisioning, str):
                if len(
                    provisioning
                ) < MINIMUM_QR_STRING_LENGTH or not provisioning.startswith("90"):
                    raise ValueError(
                        f"QR code string must be at least {MINIMUM_QR_STRING_LENGTH} "
                        "characters long and start with `90`"
                    )
                options["provisioning"] = provisioning
            # If we get a Smart Start QR code, we provision the node and return because
            # inclusion is over
            elif (
                isinstance(provisioning, QRProvisioningInformation)
                and provisioning.version == QRCodeVersion.SMART_START
            ):
                raise ValueError(
                    "Smart Start QR codes can't use the normal inclusion process. Use "
                    "the provision_smart_start_node command to provision this device."
                )
            # Otherwise we assume the data is ProvisioningEntry or
            # QRProvisioningInformation that is not a Smart Start QR code
            else:
                options["provisioning"] = provisioning.to_dict()

        if dsk is not None:
            if inclusion_strategy != InclusionStrategy.SECURITY_S2:
                raise ValueError(
                    "`dsk` option is only supported with inclusion_strategy=SECURITY_S2"
                )

            require_schema = 25
            options["dsk"] = dsk

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
        provisioning_info: ProvisioningEntry | QRProvisioningInformation | str,
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
                "entry": (
                    provisioning_info
                    if isinstance(provisioning_info, str)
                    else provisioning_info.to_dict()
                ),
            },
            require_schema=11,
        )

    async def async_unprovision_smart_start_node(
        self, dsk_or_node_id: int | str
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
        self, dsk_or_node_id: int | str
    ) -> ProvisioningEntry | None:
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

    async def async_get_provisioning_entries(self) -> list[ProvisioningEntry]:
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

    async def async_cancel_secure_bootstrap_s2(self) -> None:
        """Send cancelSecureBootstrapS2 command to Controller."""
        await self.client.async_send_command(
            {"command": "controller.cancel_secure_bootstrap_s2"}, require_schema=40
        )

    async def async_begin_exclusion(
        self, strategy: ExclusionStrategy | None = None
    ) -> bool:
        """Send beginExclusion command to Controller."""
        payload: dict[str, str | dict[str, ExclusionStrategy]] = {
            "command": "controller.begin_exclusion"
        }
        if strategy is not None:
            payload["options"] = {"strategy": strategy}
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
        force_security: bool | None = None,
        provisioning: str | ProvisioningEntry | QRProvisioningInformation | None = None,
    ) -> bool:
        """Send replaceFailedNode command to Controller."""
        # Most functionality was introduced in Schema 8
        require_schema = 8
        options: dict[str, Any] = {"strategy": inclusion_strategy}
        # forceSecurity can only be used with the default inclusion strategy
        if force_security is not None:
            if inclusion_strategy != InclusionStrategy.DEFAULT:
                raise ValueError(
                    "`forceSecurity` option is only supported with inclusion_strategy="
                    "DEFAULT"
                )
            options["forceSecurity"] = force_security

        # provisioning can only be used with the S2 inclusion strategy and may need
        # additional processing
        if provisioning is not None:
            if inclusion_strategy != InclusionStrategy.SECURITY_S2:
                raise ValueError(
                    "`provisioning` option is only supported with inclusion_strategy="
                    "SECURITY_S2"
                )
            # Provisioning option was introduced in Schema 11
            require_schema = 11
            # String is assumed to be the QR code string so we can pass as is
            if isinstance(provisioning, str):
                if len(
                    provisioning
                ) < MINIMUM_QR_STRING_LENGTH or not provisioning.startswith("90"):
                    raise ValueError(
                        f"QR code string must be at least {MINIMUM_QR_STRING_LENGTH} "
                        "characters long and start with `90`"
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

    async def async_rebuild_node_routes(self, node: Node) -> bool:
        """Send rebuildNodeRoutes command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.rebuild_node_routes", "nodeId": node.node_id},
            require_schema=32,
        )
        return cast(bool, data["success"])

    async def async_begin_rebuilding_routes(
        self, options: RebuildRoutesOptions | None = None
    ) -> bool:
        """Send beginRebuildingRoutes command to Controller."""
        msg: dict[str, str | RebuildRoutesOptionsDataType] = {
            "command": "controller.begin_rebuilding_routes"
        }
        if options:
            msg["options"] = options.to_dict()
        data = await self.client.async_send_command(msg, require_schema=32)
        return cast(bool, data["success"])

    async def async_stop_rebuilding_routes(self) -> bool:
        """Send stopRebuildingRoutes command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.stop_rebuilding_routes"}, require_schema=32
        )
        success = cast(bool, data["success"])
        if success:
            self._rebuild_routes_progress = None
            self.data["isRebuildingRoutes"] = False
        return success

    async def async_is_failed_node(self, node: Node) -> bool:
        """Send isFailedNode command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.is_failed_node", "nodeId": node.node_id}
        )
        return cast(bool, data["failed"])

    async def async_get_association_groups(
        self, source: AssociationAddress
    ) -> dict[int, AssociationGroup]:
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
    ) -> dict[int, list[AssociationAddress]]:
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
                    self,
                    node_id=association_address["nodeId"],
                    endpoint=association_address.get("endpoint"),
                )
                for association_address in association_addresses
            ]
        return associations

    async def async_check_association(
        self, source: AssociationAddress, group: int, association: AssociationAddress
    ) -> AssociationCheckResult:
        """Send checkAssociation command to Controller."""
        source_data = {"nodeId": source.node_id}
        if source.endpoint is not None:
            source_data["endpoint"] = source.endpoint

        association_data = {"nodeId": association.node_id}
        if association.endpoint is not None:
            association_data["endpoint"] = association.endpoint
        data = await self.client.async_send_command(
            {
                "command": "controller.check_association",
                **source_data,
                "group": group,
                "association": association_data,
            },
            require_schema=37,
        )
        return AssociationCheckResult(data["result"])

    async def async_add_associations(
        self,
        source: AssociationAddress,
        group: int,
        associations: list[AssociationAddress],
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
        associations: list[AssociationAddress],
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

    async def async_get_node_neighbors(self, node: Node) -> list[int]:
        """Send getNodeNeighbors command to Controller to get node's neighbors."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_node_neighbors",
                "nodeId": node.node_id,
            }
        )
        return cast(list[int], data["neighbors"])

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

    async def async_supports_feature(self, feature: ZwaveFeature) -> bool | None:
        """
        Send supportsFeature command to Controller.

        When None is returned it means the driver does not yet know whether the
        controller supports the input feature.
        """
        data = await self.client.async_send_command(
            {"command": "controller.supports_feature", "feature": feature.value},
            require_schema=12,
        )
        return cast(bool | None, data.get("supported"))

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

    async def async_restore_nvm(
        self, file: bytes, options: dict[str, bool] | None = None
    ) -> None:
        """Send restoreNVM command to Controller."""
        await self.client.async_send_command(
            {
                "command": "controller.restore_nvm",
                "nvmData": convert_bytes_to_base64(file),
                "migrateOptions": {} if options is None else options,
            },
            require_schema=42,
        )

    async def async_backup_nvm_raw_base64(self) -> str:
        """Send backupNVMRaw command to Controller and return base64 string directly."""
        data = await self.client.async_send_command(
            {"command": "controller.backup_nvm_raw"}, require_schema=14
        )
        return data["nvmData"]

    async def async_restore_nvm_base64(
        self, base64_data: str, options: dict[str, bool] | None = None
    ) -> None:
        """Send restoreNVM command to Controller with base64 data directly."""
        await self.client.async_send_command(
            {
                "command": "controller.restore_nvm",
                "nvmData": base64_data,
                "migrateOptions": {} if options is None else options,
            },
            require_schema=42,
        )

    async def async_get_power_level(self) -> dict[str, int]:
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

    async def async_toggle_rf(self, enable: bool) -> bool:
        """Send toggleRF command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.toggle_rf", "enable": enable}, require_schema=43
        )
        return cast(bool, data["success"])

    async def async_get_known_lifeline_routes(
        self,
    ) -> dict[Node, ControllerLifelineRoutes]:
        """Send getKnownLifelineRoutes command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.get_known_lifeline_routes"}, require_schema=16
        )

        return {
            self.nodes[int(node_id)]: ControllerLifelineRoutes(
                self.client, lifeline_routes
            )
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
        self, node: Node, api_key: str, include_prereleases: bool = True
    ) -> list[NodeFirmwareUpdateInfo]:
        """Send getAvailableFirmwareUpdates command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_available_firmware_updates",
                "nodeId": node.node_id,
                "apiKey": api_key,
                "includePrereleases": include_prereleases,
            },
            require_schema=32,
        )
        assert data
        return [NodeFirmwareUpdateInfo.from_dict(update) for update in data["updates"]]

    async def async_firmware_update_ota(
        self, node: Node, update_info: NodeFirmwareUpdateInfo
    ) -> NodeFirmwareUpdateResult:
        """Send firmwareUpdateOTA command to Controller."""
        data = await self.client.async_send_command(
            {
                "command": "controller.firmware_update_ota",
                "nodeId": node.node_id,
                "updateInfo": update_info.to_dict(),
            },
            require_schema=32,
        )
        return NodeFirmwareUpdateResult(node, data["result"])

    async def async_is_firmware_update_in_progress(self) -> bool:
        """Send isFirmwareUpdateInProgress command to Controller."""
        data = await self.client.async_send_command(
            {"command": "controller.is_firmware_update_in_progress"}, require_schema=26
        )
        return cast(bool, data["progress"])

    # Schema 45+ commands

    async def async_get_background_rssi(
        self,
    ) -> dict[str, int | None]:
        """Get background RSSI noise levels for all channels."""
        data = await self.client.async_send_command(
            {"command": "controller.get_background_rssi"}, require_schema=45
        )
        return {
            "rssiChannel0": data["rssiChannel0"],
            "rssiChannel1": data["rssiChannel1"],
            "rssiChannel2": data.get("rssiChannel2"),
            "rssiChannel3": data.get("rssiChannel3"),
        }

    async def async_get_long_range_nodes(self) -> list[int]:
        """Get list of nodes using Z-Wave Long Range."""
        data = await self.client.async_send_command(
            {"command": "controller.get_long_range_nodes"}, require_schema=45
        )
        return list(data["nodeIds"])

    async def async_get_dsk(self) -> bytes:
        """Get the controller's DSK."""
        data = await self.client.async_send_command(
            {"command": "controller.get_dsk"}, require_schema=45
        )
        return convert_base64_to_bytes(data["dsk"])

    async def async_get_all_association_groups(
        self, node: Node
    ) -> dict[int, dict[int, AssociationGroup]]:
        """Get all association groups for a node and all its endpoints."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_all_association_groups",
                "nodeId": node.node_id,
            },
            require_schema=45,
        )
        # Result is a nested map: endpoint -> group_id -> AssociationGroup
        result: dict[int, dict[int, AssociationGroup]] = {}
        for endpoint_str, groups in data["groups"].items():
            endpoint = int(endpoint_str)
            result[endpoint] = {}
            for group_id_str, group_data in groups.items():
                group_id = int(group_id_str)
                result[endpoint][group_id] = AssociationGroup(
                    max_nodes=group_data["maxNodes"],
                    is_lifeline=group_data["isLifeline"],
                    multi_channel=group_data["multiChannel"],
                    label=group_data["label"],
                    profile=group_data.get("profile"),
                    issued_commands=group_data.get("issuedCommands", {}),
                )
        return result

    async def async_get_all_associations(
        self, node: Node
    ) -> dict[int, dict[int, list[AssociationAddress]]]:
        """Get all associations for a node and all its endpoints."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_all_associations",
                "nodeId": node.node_id,
            },
            require_schema=45,
        )
        # Result is a nested map: endpoint -> group_id -> [AssociationAddress]
        result: dict[int, dict[int, list[AssociationAddress]]] = {}
        for endpoint_key, groups in data["associations"].items():
            # endpoint_key can be "nodeId" or "nodeId:endpoint"
            if ":" in endpoint_key:
                endpoint = int(endpoint_key.split(":")[1])
            else:
                endpoint = 0
            result[endpoint] = {}
            for group_id_str, addrs in groups.items():
                group_id = int(group_id_str)
                result[endpoint][group_id] = [
                    AssociationAddress(
                        controller=self,
                        node_id=addr["nodeId"],
                        endpoint=addr.get("endpoint"),
                    )
                    for addr in addrs
                ]
        return result

    async def async_get_all_available_firmware_updates(
        self,
        api_key: str | None = None,
        include_prereleases: bool = True,
        rf_region: RFRegion | None = None,
    ) -> dict[int, list[NodeFirmwareUpdateInfo]]:
        """Get all available firmware updates for all nodes."""
        payload: dict[str, Any] = {
            "command": "controller.get_all_available_firmware_updates",
            "includePrereleases": include_prereleases,
        }
        if api_key is not None:
            payload["apiKey"] = api_key
        if rf_region is not None:
            payload["rfRegion"] = rf_region.value

        data = await self.client.async_send_command(payload, require_schema=45)
        return {
            int(node_id): [
                NodeFirmwareUpdateInfo.from_dict(update) for update in updates
            ]
            for node_id, updates in data["updates"].items()
        }

    # Network join/leave operations

    async def async_begin_joining_network(self) -> dict[str, Any]:
        """Begin joining another network (learn mode)."""
        data = await self.client.async_send_command(
            {"command": "controller.begin_joining_network"}, require_schema=45
        )
        return dict(data["result"])

    async def async_stop_joining_network(self) -> bool:
        """Stop the join network process."""
        data = await self.client.async_send_command(
            {"command": "controller.stop_joining_network"}, require_schema=45
        )
        return cast(bool, data["success"])

    async def async_begin_leaving_network(self) -> dict[str, Any]:
        """Begin leaving the network."""
        data = await self.client.async_send_command(
            {"command": "controller.begin_leaving_network"}, require_schema=45
        )
        return dict(data["result"])

    async def async_stop_leaving_network(self) -> bool:
        """Stop the leave network process."""
        data = await self.client.async_send_command(
            {"command": "controller.stop_leaving_network"}, require_schema=45
        )
        return cast(bool, data["success"])

    # Watchdog operations

    async def async_start_watchdog(self) -> bool:
        """Start the hardware watchdog."""
        data = await self.client.async_send_command(
            {"command": "controller.start_watchdog"}, require_schema=45
        )
        return cast(bool, data["success"])

    async def async_stop_watchdog(self) -> bool:
        """Stop the hardware watchdog."""
        data = await self.client.async_send_command(
            {"command": "controller.stop_watchdog"}, require_schema=45
        )
        return cast(bool, data["success"])

    # RF region extended operations

    async def async_get_supported_rf_regions(
        self, filter_subsets: bool = False
    ) -> list[RFRegion] | None:
        """Get list of supported RF regions (cached)."""
        data = await self.client.async_send_command(
            {
                "command": "controller.get_supported_rf_regions",
                "filterSubsets": filter_subsets,
            },
            require_schema=45,
        )
        regions = data.get("regions")
        if regions is None:
            return None
        return [RFRegion(r) for r in regions]

    async def async_query_supported_rf_regions(self) -> list[RFRegion]:
        """Query all supported RF regions."""
        data = await self.client.async_send_command(
            {"command": "controller.query_supported_rf_regions"}, require_schema=45
        )
        return [RFRegion(r) for r in data["regions"]]

    async def async_query_rf_region_info(self, region: RFRegion) -> dict[str, Any]:
        """Get detailed info about a specific RF region."""
        data = await self.client.async_send_command(
            {
                "command": "controller.query_rf_region_info",
                "region": region.value,
            },
            require_schema=45,
        )
        result = {
            "region": RFRegion(data["region"]),
            "supportsZWave": data["supportsZWave"],
            "supportsLongRange": data["supportsLongRange"],
        }
        if "includesRegion" in data:
            result["includesRegion"] = RFRegion(data["includesRegion"])
        return result

    # Routing operations

    async def async_assign_return_routes(
        self, node: Node, destination_node: Node
    ) -> bool:
        """Assign optimized return routes from a node to a destination."""
        data = await self.client.async_send_command(
            {
                "command": "controller.assign_return_routes",
                "nodeId": node.node_id,
                "destinationNodeId": destination_node.node_id,
            },
            require_schema=45,
        )
        return cast(bool, data["success"])

    async def async_delete_return_routes(self, node: Node) -> bool:
        """Delete return routes from a node."""
        data = await self.client.async_send_command(
            {
                "command": "controller.delete_return_routes",
                "nodeId": node.node_id,
            },
            require_schema=45,
        )
        return cast(bool, data["success"])

    async def async_assign_suc_return_routes(self, node: Node) -> bool:
        """Assign optimized return routes from a node to the SUC."""
        data = await self.client.async_send_command(
            {
                "command": "controller.assign_suc_return_routes",
                "nodeId": node.node_id,
            },
            require_schema=45,
        )
        return cast(bool, data["success"])

    async def async_delete_suc_return_routes(self, node: Node) -> bool:
        """Delete SUC return routes from a node."""
        data = await self.client.async_send_command(
            {
                "command": "controller.delete_suc_return_routes",
                "nodeId": node.node_id,
            },
            require_schema=45,
        )
        return cast(bool, data["success"])

    async def async_discover_node_neighbors(self, node: Node) -> bool:
        """Trigger neighbor discovery for a node."""
        data = await self.client.async_send_command(
            {
                "command": "controller.discover_node_neighbors",
                "nodeId": node.node_id,
            },
            require_schema=45,
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
                "Controller doesn't know how to handle/forward this event: "
                f"{event.data}"
            )

        if (event_type := event.type) not in CONTROLLER_EVENT_MODEL_MAP:
            _LOGGER.info("Unhandled controller event: %s", event_type)
            return

        CONTROLLER_EVENT_MODEL_MAP[event_type].from_dict(event.data)
        self._handle_event_protocol(event)

        event.data["controller"] = self
        self.emit(event_type, event.data)

    def handle_inclusion_failed(self, event: Event) -> None:
        """Process an inclusion failed event."""

    def handle_exclusion_failed(self, event: Event) -> None:
        """Process an exclusion failed event."""

    def handle_inclusion_started(self, event: Event) -> None:
        """Process an inclusion started event."""

    def handle_inclusion_state_changed(self, event: Event) -> None:
        """Process an inclusion state changed event."""
        self.data["inclusionState"] = event.data["state"]

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
        event.data["reason"] = RemoveNodeReason(event.data["reason"])
        event.data["node"] = self.nodes.pop(event.data["node"]["nodeId"])
        # Remove client from node since it's no longer connected to the controller
        event.data["node"].client = None

    def handle_rebuild_routes_progress(self, event: Event) -> None:
        """Process a rebuild routes progress event."""
        self._rebuild_routes_progress = self._generate_rebuild_routes_status(
            event.data["progress"]
        )
        self.data["isRebuildingRoutes"] = True

    def handle_rebuild_routes_done(self, event: Event) -> None:
        """Process a rebuild routes done event."""
        self._last_rebuild_routes_result = self._generate_rebuild_routes_status(
            event.data["result"]
        )
        self._rebuild_routes_progress = None
        self.data["isRebuildingRoutes"] = False

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

    def handle_identify(self, event: Event) -> None:
        """Process an identify event."""
        # TODO handle event for unknown node
        if node := self.nodes.get(event.data["nodeId"]):
            event.data["node"] = node

    def handle_status_changed(self, event: Event) -> None:
        """Process a status changed event."""
        self.data["status"] = event.data["status"]
        event.data["status"] = ControllerStatus(event.data["status"])

    # Schema 45+ event handlers

    def handle_network_found(self, event: Event) -> None:
        """Process a network found event."""
        # Event data already contains homeId and ownNodeId

    def handle_network_joined(self, event: Event) -> None:
        """Process a network joined event."""

    def handle_network_left(self, event: Event) -> None:
        """Process a network left event."""

    def handle_joining_network_failed(self, event: Event) -> None:
        """Process a joining network failed event."""

    def handle_leaving_network_failed(self, event: Event) -> None:
        """Process a leaving network failed event."""
