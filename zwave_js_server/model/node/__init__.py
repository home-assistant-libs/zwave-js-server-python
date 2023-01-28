"""Provide a model for the Z-Wave JS node."""
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from ...const import (
    INTERVIEW_FAILED,
    NOT_INTERVIEWED,
    CommandClass,
    NodeStatus,
    PowerLevel,
    SecurityClass,
)
from ...event import Event, EventBase
from ...exceptions import (
    FailedCommand,
    NotFoundError,
    UnparseableValue,
    UnwriteableValue,
)
from ..command_class import CommandClassInfo
from ..device_class import DeviceClass
from ..device_config import DeviceConfig
from ..endpoint import Endpoint
from ..notification import (
    EntryControlNotification,
    EntryControlNotificationDataType,
    MultilevelSwitchNotification,
    MultilevelSwitchNotificationDataType,
    NotificationNotification,
    NotificationNotificationDataType,
    PowerLevelNotification,
    PowerLevelNotificationDataType,
)
from ..value import (
    ConfigurationValue,
    MetaDataType,
    Value,
    ValueDataType,
    ValueMetadata,
    ValueNotification,
    _get_value_id_str_from_dict,
    _init_value,
)
from .data_model import NodeDataType
from .event_model import NODE_EVENT_MODEL_MAP
from .firmware import (
    NodeFirmwareUpdateCapabilities,
    NodeFirmwareUpdateCapabilitiesDataType,
    NodeFirmwareUpdateProgress,
    NodeFirmwareUpdateProgressDataType,
    NodeFirmwareUpdateResult,
    NodeFirmwareUpdateResultDataType,
)
from .health_check import (
    CheckHealthProgress,
    LifelineHealthCheckSummary,
    RouteHealthCheckSummary,
    TestPowerLevelProgress,
)
from .statistics import NodeStatistics

if TYPE_CHECKING:
    from ...client import Client


_LOGGER = logging.getLogger(__package__)


def _get_value_id_dict_from_value_data(value_data: ValueDataType) -> Dict[str, Any]:
    """Return a value ID dict from ValueDataType."""
    data = {
        "commandClass": value_data["commandClass"],
        "property": value_data["property"],
    }

    if (endpoint := value_data.get("endpoint")) is not None:
        data["endpoint"] = endpoint
    if (property_key := value_data.get("propertyKey")) is not None:
        data["propertyKey"] = property_key

    return data


class Node(EventBase):
    """Represent a Z-Wave JS node."""

    def __init__(self, client: "Client", data: NodeDataType) -> None:
        """Initialize the node."""
        super().__init__()
        self.client = client
        self.data: NodeDataType = {}
        self._device_config = DeviceConfig({})
        self._statistics = NodeStatistics(client, data.get("statistics"))
        self._firmware_update_progress: Optional[NodeFirmwareUpdateProgress] = None
        self.values: Dict[str, Union[ConfigurationValue, Value]] = {}
        self.endpoints: Dict[int, Endpoint] = {}
        self.update(data)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{type(self).__name__}(node_id={self.node_id})"

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.client.driver, self.node_id))

    def __eq__(self, other: object) -> bool:
        """Return whether this instance equals another."""
        if not isinstance(other, Node):
            return False
        return (
            self.client.driver == other.client.driver and self.node_id == other.node_id
        )

    @property
    def node_id(self) -> int:
        """Return node ID property."""
        return self.data["nodeId"]

    @property
    def index(self) -> int:
        """Return index property."""
        return self.data["index"]

    @property
    def device_class(self) -> DeviceClass:
        """Return the device_class."""
        return DeviceClass(self.data["deviceClass"])

    @property
    def installer_icon(self) -> Optional[int]:
        """Return installer icon property."""
        return self.data.get("installerIcon")

    @property
    def user_icon(self) -> Optional[int]:
        """Return user icon property."""
        return self.data.get("userIcon")

    @property
    def status(self) -> NodeStatus:
        """Return the status."""
        return NodeStatus(self.data["status"])

    @property
    def ready(self) -> Optional[bool]:
        """Return the ready."""
        return self.data.get("ready")

    @property
    def is_listening(self) -> Optional[bool]:
        """Return the is_listening."""
        return self.data.get("isListening")

    @property
    def is_frequent_listening(self) -> Optional[Union[bool, str]]:
        """Return the is_frequent_listening."""
        return self.data.get("isFrequentListening")

    @property
    def is_routing(self) -> Optional[bool]:
        """Return the is_routing."""
        return self.data.get("isRouting")

    @property
    def max_data_rate(self) -> Optional[int]:
        """Return the max_data_rate."""
        return self.data.get("maxDataRate")

    @property
    def supported_data_rates(self) -> List[int]:
        """Return the supported_data_rates."""
        return self.data.get("supportedDataRates", [])

    @property
    def is_secure(self) -> Optional[bool]:
        """Return the is_secure."""
        if (is_secure := self.data.get("isSecure")) == "unknown":
            return None
        return is_secure

    @property
    def protocol_version(self) -> Optional[int]:
        """Return the protocol_version."""
        return self.data.get("protocolVersion")

    @property
    def supports_beaming(self) -> Optional[bool]:
        """Return the supports_beaming."""
        return self.data.get("supportsBeaming")

    @property
    def supports_security(self) -> Optional[bool]:
        """Return the supports_security."""
        return self.data.get("supportsSecurity")

    @property
    def manufacturer_id(self) -> Optional[int]:
        """Return the manufacturer_id."""
        return self.data.get("manufacturerId")

    @property
    def product_id(self) -> Optional[int]:
        """Return the product_id."""
        return self.data.get("productId")

    @property
    def product_type(self) -> Optional[int]:
        """Return the product_type."""
        return self.data.get("productType")

    @property
    def firmware_version(self) -> Optional[str]:
        """Return the firmware_version."""
        return self.data.get("firmwareVersion")

    @property
    def zwave_plus_version(self) -> Optional[int]:
        """Return the zwave_plus_version."""
        return self.data.get("zwavePlusVersion")

    @property
    def zwave_plus_node_type(self) -> Optional[int]:
        """Return the zwave_plus_node_type."""
        return self.data.get("zwavePlusNodeType")

    @property
    def zwave_plus_role_type(self) -> Optional[int]:
        """Return the zwave_plus_role_type."""
        return self.data.get("zwavePlusRoleType")

    @property
    def name(self) -> Optional[str]:
        """Return the name."""
        return self.data.get("name")

    @property
    def location(self) -> Optional[str]:
        """Return the location."""
        return self.data.get("location")

    @property
    def device_config(self) -> DeviceConfig:
        """Return the device_config."""
        return self._device_config

    @property
    def label(self) -> Optional[str]:
        """Return the label."""
        return self.data.get("label")

    @property
    def device_database_url(self) -> Optional[str]:
        """Return the device database URL."""
        return self.data.get("deviceDatabaseUrl")

    @property
    def endpoint_count_is_dynamic(self) -> Optional[bool]:
        """Return the endpoint_count_is_dynamic."""
        return self.data.get("endpointCountIsDynamic")

    @property
    def endpoints_have_identical_capabilities(self) -> Optional[bool]:
        """Return the endpoints_have_identical_capabilities."""
        return self.data.get("endpointsHaveIdenticalCapabilities")

    @property
    def individual_endpoint_count(self) -> Optional[int]:
        """Return the individual_endpoint_count."""
        return self.data.get("individualEndpointCount")

    @property
    def aggregated_endpoint_count(self) -> Optional[int]:
        """Return the aggregated_endpoint_count."""
        return self.data.get("aggregatedEndpointCount")

    @property
    def interview_attempts(self) -> Optional[int]:
        """Return the interview_attempts."""
        return self.data.get("interviewAttempts")

    @property
    def interview_stage(self) -> Optional[Union[int, str]]:
        """Return the interview_stage."""
        return self.data.get("interviewStage")

    @property
    def in_interview(self) -> bool:
        """Return whether node is currently being interviewed."""
        return (
            not self.ready
            and not self.awaiting_manual_interview
            and self.interview_stage != INTERVIEW_FAILED
        )

    @property
    def awaiting_manual_interview(self) -> bool:
        """Return whether node requires a manual interview."""
        return self.interview_stage in (None, NOT_INTERVIEWED)

    @property
    def command_classes(self) -> List[CommandClassInfo]:
        """Return all CommandClasses supported on this node."""
        return self.endpoints[0].command_classes

    @property
    def statistics(self) -> NodeStatistics:
        """Return statistics property."""
        return self._statistics

    @property
    def firmware_update_progress(self) -> Optional[NodeFirmwareUpdateProgress]:
        """Return firmware update progress."""
        return self._firmware_update_progress

    @property
    def highest_security_class(self) -> Optional[SecurityClass]:
        """Return highest security class configured on the node."""
        if (security_class := self.data.get("highestSecurityClass")) is None:
            return None
        return SecurityClass(security_class)

    @property
    def is_controller_node(self) -> bool:
        """Return whether the node is a controller node."""
        return self.data["isControllerNode"]

    @property
    def keep_awake(self) -> bool:
        """Return whether the node is set to keep awake."""
        return self.data["keepAwake"]

    def update(self, data: NodeDataType) -> None:
        """Update the internal state data."""
        self.data = data
        self._device_config = DeviceConfig(self.data.get("deviceConfig", {}))
        self._statistics = NodeStatistics(self.client, self.data.get("statistics"))

        # Remove stale values
        value_ids = (_get_value_id_str_from_dict(self, val) for val in data["values"])
        self.values = {
            value_id: val
            for value_id, val in self.values.items()
            if value_id in value_ids
        }

        # Populate new values
        for val in data["values"]:
            try:
                if (value_id := _get_value_id_str_from_dict(self, val)) in self.values:
                    self.values[value_id].update(val)
                else:
                    self.values[value_id] = _init_value(self, val)
            except UnparseableValue:
                # If we can't parse the value, don't store it
                pass

        # Remove stale endpoints
        self.endpoints = {
            idx: endpoint
            for idx, endpoint in self.endpoints.items()
            if idx in (endpoint["index"] for endpoint in self.data["endpoints"])
        }

        # Add new endpoints or update existing ones
        for endpoint in self.data["endpoints"]:
            idx = endpoint["index"]
            values = {
                value_id: value
                for value_id, value in self.values.items()
                if self.index == value.endpoint
            }
            if idx in self.endpoints:
                self.endpoints[idx].update(endpoint, values)
            else:
                self.endpoints[idx] = Endpoint(
                    self.client,
                    endpoint,
                    values,
                )

    def get_command_class_values(
        self, command_class: CommandClass, endpoint: Optional[int] = None
    ) -> Dict[str, Union[ConfigurationValue, Value]]:
        """Return all values for a given command class."""
        return {
            value_id: value
            for value_id, value in self.values.items()
            if value.command_class == command_class
            and (endpoint is None or value.endpoint == endpoint)
        }

    def get_configuration_values(self) -> Dict[str, ConfigurationValue]:
        """Return all configuration values for a node."""
        return cast(
            Dict[str, ConfigurationValue],
            self.get_command_class_values(CommandClass.CONFIGURATION),
        )

    def receive_event(self, event: Event) -> None:
        """Receive an event."""
        NODE_EVENT_MODEL_MAP[event.type](**event.data)

        self._handle_event_protocol(event)
        event.data["node"] = self

        self.emit(event.type, event.data)

    async def async_send_command(
        self,
        cmd: str,
        require_schema: Optional[int] = None,
        wait_for_result: Optional[bool] = None,
        **cmd_kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a node command. For internal use only.

        If wait_for_result is not None, it will take precedence, otherwise we will decide
        to wait or not based on the node status.
        """
        kwargs = {}
        message = {"command": f"node.{cmd}", "nodeId": self.node_id, **cmd_kwargs}
        if require_schema is not None:
            kwargs["require_schema"] = require_schema

        if wait_for_result or (
            wait_for_result is None and self.status != NodeStatus.ASLEEP
        ):
            result = await self.client.async_send_command(message, **kwargs)
            return result

        await self.client.async_send_command_no_wait(message, **kwargs)
        return None

    async def async_set_value(
        self,
        val: Union[Value, str],
        new_value: Any,
        options: Optional[dict] = None,
        wait_for_result: Optional[bool] = None,
    ) -> Optional[bool]:
        """Send setValue command to Node for given value (or value_id)."""
        # a value may be specified as value_id or the value itself
        if not isinstance(val, Value):
            if val not in self.values:
                raise NotFoundError(f"Value {val} not found on node {self}")
            val = self.values[val]

        if val.metadata.writeable is False:
            raise UnwriteableValue

        cmd_args = {
            "valueId": _get_value_id_dict_from_value_data(val.data),
            "value": new_value,
        }
        if options:
            option = next(
                (
                    option
                    for option in options
                    if option not in val.metadata.value_change_options
                ),
                None,
            )
            if option is not None:
                raise NotFoundError(
                    f"Option {option} not found on value {val} on node {self}"
                )
            cmd_args["options"] = options

        # the value object needs to be send to the server
        result = await self.async_send_command(
            "set_value", **cmd_args, wait_for_result=wait_for_result
        )

        if result is None:
            return None

        return cast(bool, result["success"])

    async def async_refresh_info(self) -> None:
        """Send refreshInfo command to Node."""
        await self.async_send_command("refresh_info", wait_for_result=False)

    async def async_refresh_values(self) -> None:
        """Send refreshValues command to Node."""
        await self.async_send_command(
            "refresh_values", wait_for_result=False, require_schema=4
        )

    async def async_refresh_cc_values(self, command_class: CommandClass) -> None:
        """Send refreshCCValues command to Node."""
        await self.async_send_command(
            "refresh_cc_values",
            commandClass=command_class,
            wait_for_result=False,
            require_schema=4,
        )

    async def async_get_defined_value_ids(self) -> List[Value]:
        """Send getDefinedValueIDs command to Node."""
        data = await self.async_send_command(
            "get_defined_value_ids", wait_for_result=True
        )

        if data is None:
            # We should never reach this code
            raise FailedCommand("Command failed", "failed_command")
        return [
            _init_value(self, cast(ValueDataType, value_id))
            for value_id in data["valueIds"]
        ]

    async def async_get_value_metadata(self, val: Union[Value, str]) -> ValueMetadata:
        """Send getValueMetadata command to Node."""
        # a value may be specified as value_id or the value itself
        if not isinstance(val, Value):
            val = self.values[val]
        # the value object needs to be send to the server
        data = await self.async_send_command(
            "get_value_metadata",
            valueId=_get_value_id_dict_from_value_data(val.data),
            wait_for_result=True,
        )
        return ValueMetadata(cast(MetaDataType, data))

    async def async_get_firmware_update_capabilities(
        self,
    ) -> NodeFirmwareUpdateCapabilities:
        """Send getFirmwareUpdateCapabilities command to Node."""
        data = await self.async_send_command(
            "get_firmware_update_capabilities",
            require_schema=7,
            wait_for_result=True,
        )
        assert data
        return NodeFirmwareUpdateCapabilities(
            cast(NodeFirmwareUpdateCapabilitiesDataType, data["capabilities"])
        )

    async def async_get_firmware_update_capabilities_cached(
        self,
    ) -> NodeFirmwareUpdateCapabilities:
        """Send getFirmwareUpdateCapabilitiesCached command to Node."""
        data = await self.async_send_command(
            "get_firmware_update_capabilities_cached",
            require_schema=21,
            wait_for_result=True,
        )
        assert data
        return NodeFirmwareUpdateCapabilities(
            cast(NodeFirmwareUpdateCapabilitiesDataType, data["capabilities"])
        )

    async def async_abort_firmware_update(self) -> None:
        """Send abortFirmwareUpdate command to Node."""
        await self.async_send_command("abort_firmware_update", wait_for_result=True)

    async def async_poll_value(self, val: Union[Value, str]) -> None:
        """Send pollValue command to Node for given value (or value_id)."""
        # a value may be specified as value_id or the value itself
        if not isinstance(val, Value):
            val = self.values[val]
        await self.async_send_command(
            "poll_value",
            valueId=_get_value_id_dict_from_value_data(val.data),
            require_schema=1,
        )

    async def async_ping(self) -> bool:
        """Send ping command to Node."""
        data = (
            await self.async_send_command(
                "ping", require_schema=5, wait_for_result=True
            )
            or {}
        )
        return cast(bool, data.get("responded", False))

    async def async_invoke_cc_api(
        self,
        command_class: CommandClass,
        method_name: str,
        *args: Any,
        wait_for_result: Optional[bool] = None,
    ) -> Any:
        """Call endpoint.invoke_cc_api command."""
        return await self.endpoints[0].async_invoke_cc_api(
            command_class, method_name, *args, wait_for_result=wait_for_result
        )

    async def async_supports_cc_api(self, command_class: CommandClass) -> bool:
        """Call endpoint.supports_cc_api command."""
        return await self.endpoints[0].async_supports_cc_api(command_class)

    async def async_supports_cc(self, command_class: CommandClass) -> bool:
        """Call endpoint.supports_cc command."""
        return await self.endpoints[0].async_supports_cc(command_class)

    async def async_controls_cc(self, command_class: CommandClass) -> bool:
        """Call endpoint.controls_cc command."""
        return await self.endpoints[0].async_controls_cc(command_class)

    async def async_is_cc_secure(self, command_class: CommandClass) -> bool:
        """Call endpoint.is_cc_secure command."""
        return await self.endpoints[0].async_is_cc_secure(command_class)

    async def async_get_cc_version(self, command_class: CommandClass) -> bool:
        """Call endpoint.get_cc_version command."""
        return await self.endpoints[0].async_get_cc_version(command_class)

    async def async_get_node_unsafe(self) -> NodeDataType:
        """Call endpoint.get_node_unsafe command."""
        return await self.endpoints[0].async_get_node_unsafe()

    async def async_has_security_class(self, security_class: SecurityClass) -> bool:
        """Return whether node has the given security class."""
        data = await self.async_send_command(
            "has_security_class",
            securityClass=security_class,
            require_schema=8,
            wait_for_result=True,
        )
        assert data
        return cast(bool, data["hasSecurityClass"])

    async def async_get_highest_security_class(self) -> SecurityClass:
        """Get the highest security class that a node supports."""
        data = await self.async_send_command(
            "get_highest_security_class", require_schema=8, wait_for_result=True
        )
        assert data
        return SecurityClass(data["highestSecurityClass"])

    async def async_test_power_level(
        self, test_node: "Node", power_level: PowerLevel, test_frame_count: int
    ) -> int:
        """Send testPowerLevel command to Node."""
        data = await self.async_send_command(
            "test_powerlevel",
            testNodeId=test_node.node_id,
            powerlevel=power_level,
            testFrameCount=test_frame_count,
            require_schema=13,
            wait_for_result=True,
        )
        assert data
        return cast(int, data["framesAcked"])

    async def async_check_lifeline_health(
        self, rounds: Optional[int] = None
    ) -> LifelineHealthCheckSummary:
        """Send checkLifelineHealth command to Node."""
        kwargs = {}
        if rounds is not None:
            kwargs["rounds"] = rounds
        data = await self.async_send_command(
            "check_lifeline_health",
            require_schema=13,
            wait_for_result=True,
            **kwargs,
        )
        assert data
        return LifelineHealthCheckSummary(data["summary"])

    async def async_check_route_health(
        self, target_node: "Node", rounds: Optional[int] = None
    ) -> RouteHealthCheckSummary:
        """Send checkRouteHealth command to Node."""
        kwargs = {"targetNodeId": target_node.node_id}
        if rounds is not None:
            kwargs["rounds"] = rounds
        data = await self.async_send_command(
            "check_route_health",
            require_schema=13,
            wait_for_result=True,
            **kwargs,
        )
        assert data
        return RouteHealthCheckSummary(data["summary"])

    async def async_get_state(self) -> NodeDataType:
        """Get node state."""
        data = await self.async_send_command(
            "get_state", require_schema=14, wait_for_result=True
        )
        assert data
        return cast(NodeDataType, data["state"])

    async def async_set_name(
        self, name: str, update_cc: bool = True, wait_for_result: Optional[bool] = None
    ) -> None:
        """Set node name."""
        # If we may not potentially update the name CC, we should just wait for the
        # result because the change is local to the driver
        if not update_cc:
            wait_for_result = True
        await self.async_send_command(
            "set_name",
            name=name,
            updateCC=update_cc,
            wait_for_result=wait_for_result,
            require_schema=14,
        )
        self.data["name"] = name

    async def async_set_location(
        self,
        location: str,
        update_cc: bool = True,
        wait_for_result: Optional[bool] = None,
    ) -> None:
        """Set node location."""
        # If we may not potentially update the location CC, we should just wait for the
        # result because the change is local to the driver
        if not update_cc:
            wait_for_result = True
        await self.async_send_command(
            "set_location",
            location=location,
            updateCC=update_cc,
            wait_for_result=wait_for_result,
            require_schema=14,
        )
        self.data["location"] = location

    async def async_is_firmware_update_in_progress(self) -> bool:
        """
        Send isFirmwareUpdateInProgress command to Node.

        If `True`, a firmware update for this node is in progress.
        """
        data = await self.async_send_command(
            "is_firmware_update_in_progress", require_schema=21, wait_for_result=True
        )
        assert data
        return cast(bool, data["progress"])

    async def async_set_keep_awake(self, keep_awake: bool) -> None:
        """Set node keep awake state."""
        await self.async_send_command(
            "set_keep_awake",
            keepAwake=keep_awake,
            wait_for_result=True,
            require_schema=14,
        )
        self.data["keepAwake"] = keep_awake

    async def async_interview(self) -> None:
        """Interview node."""
        await self.async_send_command(
            "interview",
            wait_for_result=False,
            require_schema=22,
        )

    def handle_test_powerlevel_progress(self, event: Event) -> None:
        """Process a test power level progress event."""
        event.data["test_power_level_progress"] = TestPowerLevelProgress(
            event.data["acknowledged"], event.data["total"]
        )

    def handle_check_lifeline_health_progress(self, event: Event) -> None:
        """Process a check lifeline health progress event."""
        event.data["check_lifeline_health_progress"] = CheckHealthProgress(
            event.data["rounds"], event.data["totalRounds"], event.data["lastRating"]
        )

    def handle_check_route_health_progress(self, event: Event) -> None:
        """Process a check route health progress event."""
        event.data["check_route_health_progress"] = CheckHealthProgress(
            event.data["rounds"], event.data["totalRounds"], event.data["lastRating"]
        )

    def handle_wake_up(self, event: Event) -> None:
        """Process a node wake up event."""
        # pylint: disable=unused-argument
        self.data["status"] = NodeStatus.AWAKE

    def handle_sleep(self, event: Event) -> None:
        """Process a node sleep event."""
        # pylint: disable=unused-argument
        self.data["status"] = NodeStatus.ASLEEP

    def handle_dead(self, event: Event) -> None:
        """Process a node dead event."""
        # pylint: disable=unused-argument
        self.data["status"] = NodeStatus.DEAD

    def handle_alive(self, event: Event) -> None:
        """Process a node alive event."""
        # pylint: disable=unused-argument
        self.data["status"] = NodeStatus.ALIVE

    def handle_interview_started(self, event: Event) -> None:
        """Process a node interview started event."""
        # pylint: disable=unused-argument
        self.data["ready"] = False
        self.data["interviewStage"] = None

    def handle_interview_stage_completed(self, event: Event) -> None:
        """Process a node interview stage completed event."""
        self.data["interviewStage"] = event.data["stageName"]

    def handle_interview_failed(self, event: Event) -> None:
        """Process a node interview failed event."""
        # pylint: disable=unused-argument
        self.data["interviewStage"] = INTERVIEW_FAILED

    def handle_interview_completed(self, event: Event) -> None:
        """Process a node interview completed event."""
        # pylint: disable=unused-argument
        self.data["ready"] = True

    def handle_ready(self, event: Event) -> None:
        """Process a node ready event."""
        # the event contains a full dump of the node
        self.update(event.data["nodeState"])

    def handle_value_added(self, event: Event) -> None:
        """Process a node value added event."""
        self.handle_value_updated(event)

    def value_data_idx(self, value_id: str) -> int:
        """Get the index for the given value ID in the node's value data."""
        values = self.data["values"]
        return next(
            idx
            for idx in range(len(values))
            if _get_value_id_str_from_dict(self, values[idx]) == value_id
        )

    def handle_value_updated(self, event: Event) -> None:
        """Process a node value updated event."""
        evt_val_data: ValueDataType = event.data["args"]
        value_id = _get_value_id_str_from_dict(self, evt_val_data)
        value = self.values.get(value_id)
        if value is None:
            value = _init_value(self, evt_val_data)
            self.values[value.value_id] = event.data["value"] = value
            self.data["values"].append(evt_val_data)
        else:
            value.receive_event(event)
            event.data["value"] = value
            self.data["values"][self.value_data_idx(value_id)].update(evt_val_data)

        node_val_data = self.data["values"][self.value_data_idx(value_id)]
        if "newValue" in evt_val_data:
            node_val_data["value"] = evt_val_data["newValue"]

        node_val_data.pop("newValue", None)
        node_val_data.pop("prevValue", None)

    def handle_value_removed(self, event: Event) -> None:
        """Process a node value removed event."""
        value_id = _get_value_id_str_from_dict(self, event.data["args"])
        event.data["value"] = self.values.pop(value_id)
        self.data["values"].pop(self.value_data_idx(value_id))

    def handle_value_notification(self, event: Event) -> None:
        """Process a node value notification event."""
        # if value is found, use value data as base and update what is provided
        # in the event, otherwise use the event data
        event_data = event.data["args"]
        if value := self.values.get(_get_value_id_str_from_dict(self, event_data)):
            value_notification = ValueNotification(
                self, cast(ValueDataType, dict(value.data))
            )
            value_notification.update(event_data)
        else:
            value_notification = ValueNotification(self, event_data)

        event.data["value_notification"] = value_notification

    def handle_metadata_updated(self, event: Event) -> None:
        """Process a node metadata updated event."""
        # handle metadata updated as value updated (as its a value object with
        # included metadata)
        self.handle_value_updated(event)

    def handle_notification(self, event: Event) -> None:
        """Process a node notification event."""
        command_class = CommandClass(event.data["ccId"])
        if command_class == CommandClass.NOTIFICATION:
            event.data["notification"] = NotificationNotification(
                self, cast(NotificationNotificationDataType, event.data)
            )
        elif command_class == CommandClass.SWITCH_MULTILEVEL:
            event.data["notification"] = MultilevelSwitchNotification(
                self, cast(MultilevelSwitchNotificationDataType, event.data)
            )
        elif command_class == CommandClass.ENTRY_CONTROL:
            event.data["notification"] = EntryControlNotification(
                self, cast(EntryControlNotificationDataType, event.data)
            )
        elif command_class == CommandClass.POWERLEVEL:
            event.data["notification"] = PowerLevelNotification(
                self, cast(PowerLevelNotificationDataType, event.data)
            )
        else:
            _LOGGER.info("Unhandled notification command class: %s", command_class.name)

    def handle_firmware_update_progress(self, event: Event) -> None:
        """Process a node firmware update progress event."""
        self._firmware_update_progress = event.data[
            "firmware_update_progress"
        ] = NodeFirmwareUpdateProgress(
            self, cast(NodeFirmwareUpdateProgressDataType, event.data["progress"])
        )

    def handle_firmware_update_finished(self, event: Event) -> None:
        """Process a node firmware update finished event."""
        self._firmware_update_progress = None
        event.data["firmware_update_finished"] = NodeFirmwareUpdateResult(
            self, cast(NodeFirmwareUpdateResultDataType, event.data["result"])
        )

    def handle_statistics_updated(self, event: Event) -> None:
        """Process a statistics updated event."""
        self.data["statistics"] = statistics = event.data["statistics"]
        event.data["statistics_updated"] = self._statistics = NodeStatistics(
            self.client, statistics
        )
