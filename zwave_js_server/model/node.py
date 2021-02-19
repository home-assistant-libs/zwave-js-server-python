"""Provide a model for the Z-Wave JS node."""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict, Union, cast
from zwave_js_server.const import CommandClass

from ..exceptions import UnparseableValue, UnwriteableValue
from ..event import Event, EventBase
from .device_class import DeviceClass, DeviceClassDataType
from .device_config import DeviceConfig, DeviceConfigDataType
from .endpoint import Endpoint, EndpointDataType
from .notification import Notification, NotificationDataType
from .value import (
    ConfigurationValue,
    MetaDataType,
    Value,
    ValueDataType,
    ValueMetadata,
    ValueNotification,
    _get_value_id_from_dict,
)

if TYPE_CHECKING:
    from ..client import Client


class NodeDataType(TypedDict, total=False):
    """Represent a node data dict type."""

    nodeId: int  # required
    name: str
    location: str
    status: int  # 0-4  # required
    deviceClass: DeviceClassDataType
    zwavePlusVersion: int
    nodeType: int
    roleType: int
    isListening: bool
    isFrequentListening: bool
    isRouting: bool
    maxBaudRate: int
    isSecure: bool
    isBeaming: bool
    version: int
    firmwareVersion: str
    manufacturerId: int
    productId: int
    productType: int
    deviceConfig: DeviceConfigDataType
    neighbors: List[int]
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
    values: List[ValueDataType]


class Node(EventBase):
    """Represent a Z-Wave JS node."""

    def __init__(self, client: "Client", data: NodeDataType) -> None:
        """Initialize the node."""
        super().__init__()
        self.client = client
        self.data = data
        self.values: Dict[str, Union[Value, ConfigurationValue]] = {}
        for val in data["values"]:
            value_id = _get_value_id_from_dict(self, val)
            try:
                if val["commandClass"] == CommandClass.CONFIGURATION:
                    self.values[value_id] = ConfigurationValue(self, val)
                else:
                    self.values[value_id] = Value(self, val)
            except UnparseableValue:
                # If we can't parse the value, don't store it
                pass

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{type(self).__name__}(node_id={self.node_id})"

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
    def status(self) -> int:
        """Return the status."""
        return self.data["status"]

    @property
    def ready(self) -> Optional[bool]:
        """Return the ready."""
        return self.data.get("ready")

    @property
    def device_class(self) -> DeviceClass:
        """Return the device_class."""
        return DeviceClass(self.data.get("deviceClass", {}))

    @property
    def is_listening(self) -> Optional[bool]:
        """Return the is_listening."""
        return self.data.get("isListening")

    @property
    def is_frequent_listening(self) -> Optional[bool]:
        """Return the is_frequent_listening."""
        return self.data["isFrequentListening"]

    @property
    def is_routing(self) -> Optional[bool]:
        """Return the is_routing."""
        return self.data.get("isRouting")

    @property
    def max_baud_rate(self) -> Optional[int]:
        """Return the max_baud_rate."""
        return self.data.get("maxBaudRate")

    @property
    def is_secure(self) -> Optional[bool]:
        """Return the is_secure."""
        return self.data.get("isSecure")

    @property
    def version(self) -> Optional[int]:
        """Return the version."""
        return self.data.get("version")

    @property
    def is_beaming(self) -> Optional[bool]:
        """Return the is_beaming."""
        return self.data.get("isBeaming")

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
    def node_type(self) -> Optional[int]:
        """Return the node_type."""
        return self.data.get("nodeType")

    @property
    def role_type(self) -> Optional[int]:
        """Return the role_type."""
        return self.data.get("roleType")

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
        return DeviceConfig(self.data.get("deviceConfig", {}))

    @property
    def label(self) -> Optional[str]:
        """Return the label."""
        return self.data.get("label")

    @property
    def neighbors(self) -> List[int]:
        """Return the neighbors."""
        return self.data.get("neighbors", [])

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

    async def async_set_value(self, val: Union[Value, str], new_value: Any) -> bool:
        """Send setValue command to Node for given value (or value_id)."""
        # a value may be specified as value_id or the value itself
        if not isinstance(val, Value):
            val = self.values[val]

        if val.metadata.writeable is False:
            raise UnwriteableValue

        # the value object needs to be send to the server
        result = await self.client.async_send_command(
            {
                "command": "node.set_value",
                "nodeId": self.node_id,
                "valueId": val.data,
                "value": new_value,
            }
        )
        return cast(bool, result["success"])

    async def async_refresh_info(self) -> None:
        """Send refreshInfo command to Node."""
        await self.client.async_send_command(
            {
                "command": "node.refresh_info",
                "nodeId": self.node_id,
            }
        )

    async def async_get_defined_value_ids(self) -> List[Value]:
        """Send getDefinedValueIDs command to Node."""
        data = await self.client.async_send_command(
            {
                "command": "node.get_defined_value_ids",
                "nodeId": self.node_id,
            }
        )
        return [
            Value(self, cast(ValueDataType, valueId)) for valueId in data["valueIds"]
        ]

    async def async_get_value_metadata(self, val: Union[Value, str]) -> ValueMetadata:
        """Send getValueMetadata command to Node."""
        # a value may be specified as value_id or the value itself
        if not isinstance(val, Value):
            val = self.values[val]
        # the value object needs to be send to the server
        data = await self.client.async_send_command(
            {
                "command": "node.get_value_metadata",
                "nodeId": self.node_id,
                "valueId": val.data,
            }
        )
        return ValueMetadata(cast(MetaDataType, data))

    async def async_abort_firmware_update(self) -> None:
        """Send abortFirmwareUpdate command to Node."""
        await self.client.async_send_command(
            {
                "command": "node.abort_firmware_update",
                "nodeId": self.node_id,
            }
        )

    async def async_poll_value(self, val: Union[Value, str]) -> Any:
        """Send pollValue command to Node for given value (or value_id)."""
        # a value may be specified as value_id or the value itself
        if not isinstance(val, Value):
            val = self.values[val]
        # the value object needs to be send to the server
        result = await self.client.async_send_command(
            {"command": "node.poll_value", "nodeId": self.node_id, "valueId": val.data}
        )
        # result may or may not be there
        return result.get("result")

    def handle_wake_up(self, event: Event) -> None:
        """Process a node wake up event."""

    def handle_sleep(self, event: Event) -> None:
        """Process a node sleep event."""

    def handle_dead(self, event: Event) -> None:
        """Process a node dead event."""

    def handle_alive(self, event: Event) -> None:
        """Process a node alive event."""

    def handle_interview_completed(self, event: Event) -> None:
        """Process a node interview completed event."""

    def handle_interview_failed(self, event: Event) -> None:
        """Process a node interview failed event."""

    def handle_ready(self, event: Event) -> None:
        """Process a node ready event."""
        # the event contains a full dump of the node
        self.data.update(event.data["nodeState"])
        # update/add values
        for value_state in event.data["nodeState"]["values"]:
            value_id = _get_value_id_from_dict(self, value_state)
            value = self.values.get(value_id)
            if value is None:
                self.values[value_id] = Value(self, value_state)
            else:
                value.update(value_state)

    def handle_value_added(self, event: Event) -> None:
        """Process a node value added event."""
        value = Value(self, event.data["args"])
        self.values[value.value_id] = event.data["value"] = value

    def handle_value_updated(self, event: Event) -> None:
        """Process a node value updated event."""
        value = self.values.get(_get_value_id_from_dict(self, event.data["args"]))
        if value is None:
            # received update for unknown value
            # should not happen but just in case, treat like added value
            self.handle_value_added(event)
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
        # append metadata if value metadata is available
        value = self.values.get(_get_value_id_from_dict(self, event.data["args"]))
        if value and value.data.get("metadata"):
            event.data["args"]["metadata"] = value.data["metadata"]
        event.data["value_notification"] = ValueNotification(self, event.data["args"])

    def handle_metadata_updated(self, event: Event) -> None:
        """Process a node metadata updated event."""
        # handle metadata updated as value updated (a its a value object with included metadata)
        self.handle_value_updated(event)

    def handle_notification(self, event: Event) -> None:
        """Process a node notification event."""
        event.data["notification"] = Notification(
            self, cast(NotificationDataType, event.data)
        )

    def handle_firmware_update_progress(self, event: Event) -> None:
        """Process a node firmware update progress event."""

    def handle_firmware_update_finished(self, event: Event) -> None:
        """Process a node firmware update finished event."""
