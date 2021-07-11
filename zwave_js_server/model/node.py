"""Provide a model for the Z-Wave JS node."""
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict, Union, cast

from ..const import CommandClass, INTERVIEW_FAILED
from ..event import Event, EventBase
from ..exceptions import FailedCommand, UnparseableValue, UnwriteableValue
from .command_class import CommandClassInfo, CommandClassInfoDataType
from .device_class import DeviceClass, DeviceClassDataType
from .device_config import DeviceConfig, DeviceConfigDataType
from .endpoint import Endpoint, EndpointDataType
from .firmware import (
    FirmwareUpdateFinished,
    FirmwareUpdateFinishedDataType,
    FirmwareUpdateProgress,
    FirmwareUpdateProgressDataType,
)
from .notification import (
    EntryControlNotification,
    EntryControlNotificationDataType,
    NotificationNotification,
    NotificationNotificationDataType,
)
from .value import (
    ConfigurationValue,
    MetaDataType,
    Value,
    ValueDataType,
    ValueMetadata,
    ValueNotification,
    _get_value_id_from_dict,
    _init_value,
)

if TYPE_CHECKING:
    from ..client import Client


class NodeStatus(IntEnum):
    """Enum with all Node status values.

    https://zwave-js.github.io/node-zwave-js/#/api/node?id=status
    """

    UNKNOWN = 0
    ASLEEP = 1
    AWAKE = 2
    DEAD = 3
    ALIVE = 4


class NodeDataType(TypedDict, total=False):
    """Represent a node data dict type."""

    nodeId: int  # required
    name: str
    location: str
    status: int  # 0-4  # required
    deviceClass: DeviceClassDataType
    zwavePlusVersion: int
    zwavePlusNodeType: int
    zwavePlusRoleType: int
    isListening: bool
    isFrequentListening: Union[bool, str]
    isRouting: bool
    maxDataRate: int
    supportedDataRates: List[int]
    isSecure: bool
    supportsBeaming: bool
    supportsSecurity: bool
    protocolVersion: int
    firmwareVersion: str
    manufacturerId: int
    productId: int
    productType: int
    deviceConfig: DeviceConfigDataType
    deviceDatabaseUrl: str
    keepAwake: bool
    index: int
    installerIcon: int
    userIcon: int
    ready: bool
    label: str
    endpoints: List[EndpointDataType]
    endpointCountIsDynamic: bool
    endpointsHaveIdenticalCapabilities: bool
    individualEndpointCount: int
    aggregatedEndpointCount: int
    interviewAttempts: int
    interviewStage: Optional[Union[int, str]]
    commandClasses: List[CommandClassInfoDataType]
    values: List[ValueDataType]


class Node(EventBase):
    """Represent a Z-Wave JS node."""

    def __init__(self, client: "Client", data: NodeDataType) -> None:
        """Initialize the node."""
        super().__init__()
        self.client = client
        self.data = data
        self._device_config = DeviceConfig(self.data.get("deviceConfig", {}))
        self.values: Dict[str, Union[Value, ConfigurationValue]] = {}
        for val in data["values"]:
            value_id = _get_value_id_from_dict(self, val)
            try:
                self.values[value_id] = _init_value(self, val)
            except UnparseableValue:
                # If we can't parse the value, don't store it
                pass

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
        """Return the node_id."""
        return self.data["nodeId"]

    @property
    def index(self) -> Optional[int]:
        """Return the index."""
        return self.data.get("index")

    @property
    def installer_icon(self) -> Optional[int]:
        """Return the installer_icon."""
        return self.data.get("installerIcon")

    @property
    def user_icon(self) -> Optional[int]:
        """Return the user_icon."""
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
    def device_class(self) -> DeviceClass:
        """Return the device_class."""
        return DeviceClass(self.data["deviceClass"])

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
        return self.data.get("isSecure")

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
    def endpoints(self) -> List[Endpoint]:
        """Return the endpoints."""
        return [Endpoint(endpoint) for endpoint in self.data["endpoints"]]

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
        return not self.ready and self.interview_stage != INTERVIEW_FAILED

    @property
    def command_classes(self) -> List[CommandClassInfo]:
        """Return all CommandClasses supported on this node."""
        return [CommandClassInfo(cc) for cc in self.data["commandClasses"]]

    def get_command_class_values(
        self, command_class: CommandClass, endpoint: int = None
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

        If wait_for_result is not None, it will take precedence, otherwise we will decide to wait
        or not based on the node status.
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
        options: dict = None,
        wait_for_result: Optional[bool] = None,
    ) -> Optional[bool]:
        """Send setValue command to Node for given value (or value_id)."""
        # a value may be specified as value_id or the value itself
        if not isinstance(val, Value):
            val = self.values[val]

        if val.metadata.writeable is False:
            raise UnwriteableValue

        cmd_args = {
            "valueId": val.data,
            "value": new_value,
        }
        if options:
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
            "get_value_metadata", valueId=val.data, wait_for_result=True
        )
        return ValueMetadata(cast(MetaDataType, data))

    async def async_abort_firmware_update(self) -> None:
        """Send abortFirmwareUpdate command to Node."""
        await self.async_send_command("abort_firmware_update", wait_for_result=False)

    async def async_poll_value(self, val: Union[Value, str]) -> None:
        """Send pollValue command to Node for given value (or value_id)."""
        # a value may be specified as value_id or the value itself
        if not isinstance(val, Value):
            val = self.values[val]
        await self.async_send_command("poll_value", valueId=val.data, require_schema=1)

    async def async_ping(self) -> bool:
        """Send ping command to Node."""
        data = (
            await self.async_send_command(
                "ping", require_schema=5, wait_for_result=True
            )
            or {}
        )
        return cast(bool, data.get("responded", False))

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
        self.data.update(event.data["nodeState"])
        # update device config
        if new_device_config := self.data.get("deviceConfig"):
            self._device_config = DeviceConfig(new_device_config)
        # update/add values
        for value_state in event.data["nodeState"]["values"]:
            value_id = _get_value_id_from_dict(self, value_state)
            value = self.values.get(value_id)
            if value is None:
                self.values[value_id] = _init_value(self, value_state)
            else:
                value.update(value_state)

    def handle_value_added(self, event: Event) -> None:
        """Process a node value added event."""
        self.handle_value_updated(event)

    def handle_value_updated(self, event: Event) -> None:
        """Process a node value updated event."""
        value = self.values.get(_get_value_id_from_dict(self, event.data["args"]))
        if value is None:
            value = _init_value(self, event.data["args"])
            self.values[value.value_id] = event.data["value"] = value
        else:
            value.receive_event(event)
            event.data["value"] = value

    def handle_value_removed(self, event: Event) -> None:
        """Process a node value removed event."""
        event.data["value"] = self.values.pop(
            _get_value_id_from_dict(self, event.data["args"])
        )

    def handle_value_notification(self, event: Event) -> None:
        """Process a node value notification event."""
        # if value is found, use value data as base and update what is provided
        # in the event, otherwise use the event data
        event_data = event.data["args"]
        if value := self.values.get(_get_value_id_from_dict(self, event_data)):
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
        if event.data["ccId"] == CommandClass.NOTIFICATION.value:
            event.data["notification"] = NotificationNotification(
                self, cast(NotificationNotificationDataType, event.data)
            )
        else:
            event.data["notification"] = EntryControlNotification(
                self, cast(EntryControlNotificationDataType, event.data)
            )

    def handle_firmware_update_progress(self, event: Event) -> None:
        """Process a node firmware update progress event."""
        event.data["firmware_update_progress"] = FirmwareUpdateProgress(
            self, cast(FirmwareUpdateProgressDataType, event.data)
        )

    def handle_firmware_update_finished(self, event: Event) -> None:
        """Process a node firmware update finished event."""
        event.data["firmware_update_finished"] = FirmwareUpdateFinished(
            self, cast(FirmwareUpdateFinishedDataType, event.data)
        )
