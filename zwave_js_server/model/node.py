"""Provide a model for the Z-Wave JS node."""
from typing import TYPE_CHECKING, Any, List, Optional, TypedDict, Union, cast

from ..event import Event, EventBase
from .device_class import DeviceClass, DeviceClassDataType
from .device_config import DeviceConfig, DeviceConfigDataType
from .value import (
    MetaDataType,
    Value,
    ValueDataType,
    ValueMetadata,
    ValueNotification,
    get_value_id,
)

if TYPE_CHECKING:
    from ..client import Client


class NodeDataType(TypedDict, total=False):
    """Represent a node data dict type."""

    nodeId: int  # required
    name: str
    location: str
    status: int  # 0-4  # required
    deviceClass: DeviceClassDataType  # required
    zwavePlusVersion: int
    nodeType: int
    roleType: int
    isListening: bool  # required
    isFrequentListening: bool  # required
    isRouting: bool  # required
    maxBaudRate: int  # required
    isSecure: bool  # required
    isBeaming: bool  # required
    version: int  # required
    firmwareVersion: str
    manufacturerId: int  # required
    productId: int  # required
    productType: int  # required
    deviceConfig: DeviceConfigDataType
    neighbors: List[int]  # required
    keepAwake: bool  # required
    index: int  # TODO: I can't the below items in the docs.
    installerIcon: int
    userIcon: int
    ready: bool
    label: str
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
        self.values = {
            get_value_id(self, val): Value(self, val) for val in data["values"]
        }

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
        return self.data.get("ready")  # TODO: I can't find ready in the docs.

    @property
    def device_class(self) -> DeviceClass:
        """Return the device_class."""
        return DeviceClass(self.data["deviceClass"])

    @property
    def is_listening(self) -> bool:
        """Return the is_listening."""
        return self.data["isListening"]

    @property
    def is_frequent_listening(self) -> bool:
        """Return the is_frequent_listening."""
        return self.data["isFrequentListening"]

    @property
    def is_routing(self) -> bool:
        """Return the is_routing."""
        return self.data["isRouting"]

    @property
    def max_baud_rate(self) -> int:
        """Return the max_baud_rate."""
        return self.data["maxBaudRate"]

    @property
    def is_secure(self) -> bool:
        """Return the is_secure."""
        return self.data["isSecure"]

    @property
    def version(self) -> int:
        """Return the version."""
        return self.data["version"]

    @property
    def is_beaming(self) -> bool:
        """Return the is_beaming."""
        return self.data["isBeaming"]

    @property
    def manufacturer_id(self) -> int:
        """Return the manufacturer_id."""
        return self.data["manufacturerId"]

    @property
    def product_id(self) -> int:
        """Return the product_id."""
        return self.data["productId"]

    @property
    def product_type(self) -> int:
        """Return the product_type."""
        return self.data["productType"]

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
        return self.data["neighbors"]

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
        await self.client.async_send_json_message(
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
        await self.client.async_send_json_message(
            {
                "command": "node.abort_firmware_update",
                "nodeId": self.node_id,
            }
        )

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

    def handle_value_added(self, event: Event) -> None:
        """Process a node value added event."""
        value = Value(self, event.data["args"])
        self.values[value.value_id] = event.data["value"] = value

    def handle_value_updated(self, event: Event) -> None:
        """Process a node value updated event."""
        value = self.values.get(get_value_id(self, event.data["args"]))
        if value is None:
            # TODO decide how to handle value updated for unknown values
            print()
            print(
                "Value updated for unknown value",
                get_value_id(self, event.data["args"]),
            )
            print("Available value IDs", ", ".join(self.values))
            print()
            value = Value(self, event.data["args"])
            self.values[value.value_id] = value
        else:
            value.receive_event(event)
        event.data["value"] = value

    def handle_value_removed(self, event: Event) -> None:
        """Process a node value removed event."""
        event.data["value"] = self.values.pop(get_value_id(self, event.data["args"]))

    def handle_value_notification(self, event: Event) -> None:
        """Process a node value notification event."""
        event.data["notification"] = ValueNotification.from_event(event)

    def handle_metadata_updated(self, event: Event) -> None:
        """Process a node metadata updated event."""

    def handle_notification(self, event: Event) -> None:
        """Process a node notification event."""

    def handle_firmware_update_progress(self, event: Event) -> None:
        """Process a node firmware update progress event."""

    def handle_firmware_update_finished(self, event: Event) -> None:
        """Process a node firmware update finished event."""
