"""Test the node model."""

import asyncio
from copy import deepcopy
from datetime import UTC, datetime
import json
import logging
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from zwave_js_server.const import (
    INTERVIEW_FAILED,
    CommandClass,
    CommandStatus,
    NodeStatus,
    PowerLevel,
    ProtocolDataRate,
    ProtocolVersion,
    Protocols,
    RFRegion,
    SecurityClass,
    SupervisionStatus,
    Weekday,
)
from zwave_js_server.const.command_class.battery import BatteryReplacementStatus
from zwave_js_server.const.command_class.entry_control import (
    EntryControlDataType,
    EntryControlEventType,
)
from zwave_js_server.const.command_class.multilevel_switch import (
    MultilevelSwitchCommand,
)
from zwave_js_server.const.command_class.notification import (
    AccessControlNotificationEvent,
    NotificationType,
)
from zwave_js_server.const.command_class.power_level import PowerLevelTestStatus
from zwave_js_server.event import Event
from zwave_js_server.exceptions import (
    FailedCommand,
    NotFoundError,
    RssiErrorReceived,
    UnwriteableValue,
)
from zwave_js_server.model import endpoint as endpoint_pkg, node as node_pkg
from zwave_js_server.model.node import Node
from zwave_js_server.model.node.firmware import (
    NodeFirmwareUpdateInfo,
    NodeFirmwareUpdateStatus,
)
from zwave_js_server.model.node.health_check import (
    LifelineHealthCheckResultDataType,
    RouteHealthCheckResultDataType,
)
from zwave_js_server.model.node.statistics import NodeStatistics
from zwave_js_server.model.value import (
    ConfigurationValue,
    ConfigurationValueFormat,
    SetConfigParameterResult,
    get_value_id_str,
)

from .. import load_fixture

# pylint: disable=unused-argument

FIRMWARE_UPDATE_INFO = {
    "version": "1.0.0",
    "changelog": "changelog",
    "channel": "stable",
    "files": [{"target": 0, "url": "http://example.com", "integrity": "test"}],
    "downgrade": True,
    "normalizedVersion": "1.0.0",
    "device": {
        "manufacturerId": 1,
        "productType": 2,
        "productId": 3,
        "firmwareVersion": "0.4.4",
        "rfRegion": 1,
    },
}


def test_firmware():
    """Test NodeFirmwareUpdateInfo."""
    firmware_update_info = NodeFirmwareUpdateInfo.from_dict(FIRMWARE_UPDATE_INFO)
    assert firmware_update_info.version == "1.0.0"
    assert firmware_update_info.changelog == "changelog"
    assert firmware_update_info.channel == "stable"
    assert len(firmware_update_info.files) == 1
    assert firmware_update_info.files[0].target == 0
    assert firmware_update_info.files[0].url == "http://example.com"
    assert firmware_update_info.files[0].integrity == "test"
    assert firmware_update_info.downgrade
    assert firmware_update_info.normalized_version == "1.0.0"
    assert firmware_update_info.device.manufacturer_id == 1
    assert firmware_update_info.device.product_type == 2
    assert firmware_update_info.device.product_id == 3
    assert firmware_update_info.device.firmware_version == "0.4.4"
    assert firmware_update_info.device.rf_region == RFRegion.USA
    assert firmware_update_info.to_dict() == FIRMWARE_UPDATE_INFO


def test_from_state(client):
    """Test from_state method."""
    state = json.loads(load_fixture("basic_dump.txt").split("\n")[0])["result"]["state"]

    node = node_pkg.Node(client, state["nodes"][0])

    assert node.node_id == 1
    assert node.index == 0
    assert node.status == 4
    assert node.ready is True
    assert node.device_class.basic.key == 2
    assert node.device_class.generic.label == "Static Controller"

    assert node.is_listening is True
    assert node.is_frequent_listening is False
    assert node.is_routing is False
    assert node.max_data_rate == 100000
    assert node.supported_data_rates == [40000, 100000]
    assert node.is_secure is False
    assert node.protocol is None
    assert node.protocol_version == ProtocolVersion.VERSION_4_5X_OR_6_0X
    assert node.supports_beaming is True
    assert node.supports_security is False
    assert node.zwave_plus_node_type is None
    assert node.zwave_plus_role_type is None
    assert node.manufacturer_id == 134
    assert node.product_id == 90
    assert node.product_type == 257
    assert node.label == "ZW090"
    assert node.interview_attempts == 0
    assert node.installer_icon is None
    assert node.user_icon is None
    assert node.firmware_version is None
    assert node.name is None
    assert node.zwave_plus_version is None
    assert node.location is None
    assert node.endpoint_count_is_dynamic is None
    assert node.endpoints_have_identical_capabilities is None
    assert node.individual_endpoint_count is None
    assert node.aggregated_endpoint_count is None
    assert node.interview_stage == "Neighbors"
    assert not node.is_controller_node
    assert not node.keep_awake
    assert len(node.command_classes) == 0
    assert len(node.endpoints) == 1
    assert node.endpoints[0].index == 0
    assert node.endpoints[0].installer_icon is None
    assert node.endpoints[0].user_icon is None
    assert node.endpoints[0].command_classes == []
    assert node.endpoints[0].endpoint_label is None
    device_class = node.endpoints[0].device_class
    assert device_class.basic.key == 2
    assert device_class.generic.key == 2
    assert device_class.specific.key == 1
    stats = node.statistics
    assert (
        stats.commands_dropped_rx
        == stats.commands_dropped_tx
        == stats.commands_rx
        == stats.commands_tx
        == stats.timeout_response
        == 0
    )
    assert node == node_pkg.Node(client, state["nodes"][0])
    assert node != node.node_id
    assert hash(node) == hash((client.driver, node.node_id))
    assert node.endpoints[0] == endpoint_pkg.Endpoint(
        client, node, state["nodes"][0]["endpoints"][0], {}
    )
    assert node.endpoints[0] != node.endpoints[0].index
    assert hash(node.endpoints[0]) == hash((client.driver, node.node_id, 0))
    assert node.last_seen is None
    event = Event(
        "statistics updated",
        {
            "source": "node",
            "event": "statistics updated",
            "nodeId": node.node_id,
            "statistics": {
                "commandsTX": 1,
                "commandsRX": 2,
                "commandsDroppedTX": 3,
                "commandsDroppedRX": 4,
                "timeoutResponse": 5,
                "rssi": 7,
                "lastSeen": "2023-07-18T15:42:34.701Z",
            },
        },
    )
    node.receive_event(event)
    assert node.last_seen == datetime(2023, 7, 18, 15, 42, 34, 701000, UTC)


async def test_last_seen(lock_schlage_be469):
    """Test last seen property."""
    assert lock_schlage_be469.last_seen == datetime(
        2023, 7, 18, 15, 42, 34, 701000, UTC
    )
    assert (
        lock_schlage_be469.last_seen
        == lock_schlage_be469.statistics.last_seen
        == datetime.fromisoformat(lock_schlage_be469.statistics.data.get("lastSeen"))
    )


async def test_highest_security_value(lock_schlage_be469, ring_keypad):
    """Test the highest_security_class property."""
    assert lock_schlage_be469.highest_security_class == SecurityClass.S0_LEGACY
    assert ring_keypad.highest_security_class is None


async def test_command_classes(endpoints_with_command_classes: Node) -> None:
    """Test command_classes property on endpoint."""
    node = endpoints_with_command_classes
    assert len(node.endpoints[0].command_classes) == 17
    command_class_info = node.endpoints[0].command_classes[0]
    assert command_class_info.id == 38
    assert command_class_info.command_class == CommandClass.SWITCH_MULTILEVEL
    assert command_class_info.name == "Multilevel Switch"
    assert command_class_info.version == 2
    assert command_class_info.is_secure is False
    assert command_class_info.to_dict() == command_class_info.data


async def test_device_config(
    wallmote_central_scene, climate_radio_thermostat_ct100_plus
):
    """Test a device config."""
    node: node_pkg.Node = wallmote_central_scene

    device_config = node.device_config
    assert device_config.is_embedded
    assert device_config.filename == (
        "/usr/src/app/node_modules/@zwave-js/config/config/devices/0x0086/zw130.json"
    )
    assert device_config.manufacturer == "AEON Labs"
    assert device_config.manufacturer_id == 134
    assert device_config.label == "ZW130"
    assert device_config.description == "WallMote Quad"
    assert len(device_config.devices) == 3
    assert device_config.devices[0].product_id == 130
    assert device_config.devices[0].product_type == 2
    assert device_config.firmware_version.min == "0.0"
    assert device_config.firmware_version.max == "255.255"
    assert device_config.metadata.inclusion == (
        "To add the ZP3111 to the Z-Wave network (inclusion), place the Z-Wave "
        "primary controller into inclusion mode. Press the Program Switch of ZP3111 "
        "for sending the NIF. After sending NIF, Z-Wave will send the auto inclusion, "
        "otherwise, ZP3111 will go to sleep after 20 seconds."
    )
    assert device_config.metadata.exclusion == (
        "To remove the ZP3111 from the Z-Wave network (exclusion), place the Z-Wave "
        "primary controller into \u201cexclusion\u201d mode, and following its "
        "instruction to delete the ZP3111 to the controller. Press the Program Switch "
        "of ZP3111 once to be excluded."
    )
    assert device_config.metadata.reset == (
        "Remove cover to trigged tamper switch, LED flash once & send out Alarm "
        "Report. Press Program Switch 10 times within 10 seconds, ZP3111 will send "
        "the \u201cDevice Reset Locally Notification\u201d command and reset to the "
        "factory default. (Remark: This is to be used only in the case of primary "
        "controller being inoperable or otherwise unavailable.)"
    )
    assert device_config.metadata.manual == (
        "https://products.z-wavealliance.org/ProductManual/File?folder=&filename="
        "MarketCertificationFiles/2479/ZP3111-5_R2_20170316.pdf"
    )
    assert device_config.metadata.wakeup is None
    assert device_config.metadata.comments == [{"level": "info", "text": "test"}]
    assert device_config.associations == {}
    assert device_config.param_information == {"_map": {}}
    assert device_config.supports_zwave_plus is None

    assert climate_radio_thermostat_ct100_plus.device_config.metadata.comments == []


async def test_protocol(client, wallmote_central_scene_state):
    """Test protocol of a node."""
    node_state = deepcopy(wallmote_central_scene_state)
    node_state["protocol"] = 0
    node = node_pkg.Node(client, node_state)
    assert node.protocol is Protocols.ZWAVE


async def test_endpoint_no_device_class(climate_radio_thermostat_ct100_plus):
    """Test endpoint without a device class."""
    assert climate_radio_thermostat_ct100_plus.endpoints[0].device_class is None


async def test_unknown_values(cover_qubino_shutter):
    """Test that values that are unknown return as None."""
    node = cover_qubino_shutter
    assert (
        "5-38-0-currentValue" in node.values
        and node.values["5-38-0-currentValue"].value is None
    )
    assert (
        "5-37-0-currentValue" in node.values
        and node.values["5-37-0-currentValue"].value is None
    )


async def test_device_database_url(cover_qubino_shutter):
    """Test that the device database URL is available."""
    assert (
        cover_qubino_shutter.device_database_url
        == "https://devices.zwave-js.io/?jumpTo=0x0159:0x0003:0x0053:0.0"
    )


async def test_values_without_property_key_name(multisensor_6):
    """Test that values with property key and without property key name can be found."""
    node = multisensor_6
    assert "52-112-0-101-1" in node.values
    assert "52-112-0-101-16" in node.values


async def test_hash(climate_radio_thermostat_ct100_plus):
    """Test node hash."""
    node = climate_radio_thermostat_ct100_plus
    assert hash(node) == hash((node.client.driver, node.node_id))


async def test_command_class_values(climate_radio_thermostat_ct100_plus):
    """Test node methods to get command class values."""
    node = climate_radio_thermostat_ct100_plus
    assert node.node_id == 13
    switch_values = node.get_command_class_values(CommandClass.SENSOR_MULTILEVEL)
    assert len(switch_values) == 2

    with pytest.raises(UnwriteableValue):
        await node.async_set_value("13-112-0-2", 1)


async def test_set_value(multisensor_6, uuid4, mock_command):
    """Test set value."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": True},
    )
    value_id = "52-32-0-targetValue"
    assert await node.async_set_value(value_id, 42) is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {"commandClass": 32, "endpoint": 0, "property": "targetValue"},
        "value": 42,
        "messageId": uuid4,
    }

    # Set value with options
    assert await node.async_set_value(value_id, 42, {"transitionDuration": 1}) is None

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {"commandClass": 32, "endpoint": 0, "property": "targetValue"},
        "value": 42,
        "options": {"transitionDuration": 1},
        "messageId": uuid4,
    }

    # Set value with illegal option
    with pytest.raises(NotFoundError):
        await node.async_set_value(value_id, 42, {"fake_option": 1})

    # Use invalid value
    with pytest.raises(NotFoundError):
        await node.async_set_value(f"{value_id}_fake_value", 42)


async def test_set_value_node_status_change(driver, multisensor_6_state):
    """Test set value when node status changes."""

    async def async_send_command(
        message: dict[str, Any], require_schema: int | None = None
    ) -> dict:
        """Send a mock command that never returns."""
        block_event = asyncio.Event()
        await block_event.wait()

    with patch("zwave_js_server.client.Client", autospec=True) as client_class:
        client = client_class.return_value
        client.driver = driver

    client.async_send_command = AsyncMock(side_effect=async_send_command)
    node = node_pkg.Node(client, multisensor_6_state)
    # wake up node
    event = Event(type="wake up")
    node.handle_wake_up(event)
    task = asyncio.create_task(node.async_send_command("mock_cmd"))
    task_2 = asyncio.create_task(node.endpoints[0].async_send_command("mock_cmd"))
    await asyncio.sleep(0.01)
    # we are waiting for the response
    assert not task.done()
    assert not task_2.done()
    # node goes to sleep
    event = Event(type="sleep")
    node.handle_sleep(event)
    await asyncio.sleep(0.01)
    # we are no longer waiting for the response
    assert task.done()
    assert task.result() is None
    assert task_2.done()
    assert task_2.result() is None

    # mark node as alive
    event = Event(type="alive")
    node.handle_alive(event)
    task = asyncio.create_task(node.async_send_command("mock_cmd"))
    task_2 = asyncio.create_task(node.endpoints[0].async_send_command("mock_cmd"))
    await asyncio.sleep(0.01)
    # we are waiting for the response
    assert not task.done()
    assert not task_2.done()
    # node is marked dead
    event = Event(type="dead")
    node.handle_dead(event)
    await asyncio.sleep(0.01)
    # we are no longer waiting for the response
    assert task.done()
    assert task.result() is None
    assert task_2.done()
    assert task_2.result() is None


async def test_poll_value(multisensor_6, uuid4, mock_command):
    """Test poll value."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.poll_value", "nodeId": node.node_id},
        {"result": "something"},
    )
    value_id = "52-32-0-currentValue"
    assert await node.async_poll_value(value_id) is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.poll_value",
        "nodeId": node.node_id,
        "valueId": {"commandClass": 32, "endpoint": 0, "property": "currentValue"},
        "messageId": uuid4,
    }


async def test_ping(multisensor_6, uuid4, mock_command):
    """Test ping."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.ping", "nodeId": node.node_id},
        {"responded": True},
    )
    assert await node.async_ping()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.ping",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_refresh_info(multisensor_6, uuid4, mock_command):
    """Test refresh info."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.refresh_info", "nodeId": node.node_id},
        {},
    )
    assert await node.async_refresh_info() is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.refresh_info",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_value_added_event(multisensor_6):
    """Test Node value removed event."""
    node = multisensor_6
    assert "52-112-0-2" in node.values
    event = Event(
        type="value removed",
        data={
            "source": "node",
            "event": "value removed",
            "nodeId": 52,
            "args": {
                "commandClassName": "Configuration",
                "commandClass": 112,
                "endpoint": 0,
                "property": 2,
                "propertyName": "Stay Awake in Battery Mode",
                "metadata": {
                    "type": "number",
                    "readable": True,
                    "writeable": True,
                    "valueSize": 1,
                    "min": 0,
                    "max": 1,
                    "default": 0,
                    "format": 0,
                    "allowManualEntry": False,
                    "states": {"0": "Disable", "1": "Enable"},
                    "label": "Stay Awake in Battery Mode",
                    "description": "Stay awake for 10 minutes at power on",
                    "isFromConfig": True,
                },
                "value": 0,
            },
        },
    )
    node.handle_value_removed(event)
    assert "52-112-0-2" not in node.values


async def test_get_defined_value_ids(multisensor_6, uuid4, mock_command):
    """Test get defined value ids."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.get_defined_value_ids", "nodeId": node.node_id},
        {
            "valueIds": [
                {
                    "commandClassName": "Wake Up",
                    "commandClass": 132,
                    "endpoint": 0,
                    "property": "wakeUpInterval",
                    "propertyName": "wakeUpInterval",
                },
                {
                    "commandClassName": "Wake Up",
                    "commandClass": 132,
                    "endpoint": 0,
                    "property": "controllerNodeId",
                    "propertyName": "controllerNodeId",
                },
            ]
        },
    )
    result = await node.async_get_defined_value_ids()

    assert len(result) == 2

    assert result[0].command_class_name == "Wake Up"
    assert result[0].command_class == 132
    assert result[0].endpoint == 0
    assert result[0].property_ == "wakeUpInterval"
    assert result[0].property_name == "wakeUpInterval"

    assert result[1].command_class_name == "Wake Up"
    assert result[1].command_class == 132
    assert result[1].endpoint == 0
    assert result[1].property_ == "controllerNodeId"
    assert result[1].property_name == "controllerNodeId"

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_defined_value_ids",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_get_value_metadata(multisensor_6, uuid4, mock_command):
    """Test get value metadata."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.get_value_metadata", "nodeId": node.node_id},
        {
            "type": "any",
            "readable": True,
            "writeable": False,
            "label": "Node ID of the controller",
            "description": "Description of the value metadata",
        },
    )

    result = await node.async_get_value_metadata("52-32-0-targetValue")

    assert result.type == "any"
    assert result.readable is True
    assert result.writeable is False
    assert result.label == "Node ID of the controller"
    assert result.description == "Description of the value metadata"

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_value_metadata",
        "nodeId": node.node_id,
        "valueId": {"commandClass": 32, "endpoint": 0, "property": "targetValue"},
        "messageId": uuid4,
    }

    ack_commands.clear()


async def test_abort_firmware_update(multisensor_6, uuid4, mock_command):
    """Test abort firmware update."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.abort_firmware_update", "nodeId": node.node_id},
        {},
    )

    assert await node.async_abort_firmware_update() is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.abort_firmware_update",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


def test_node_inclusion(multisensor_6_state):
    """Emulate a node being added."""
    # when a node node is added, it has minimal info first
    node = node_pkg.Node(
        None, {"nodeId": 52, "status": 1, "ready": False, "values": [], "endpoints": []}
    )
    assert node.node_id == 52
    assert node.status == 1
    assert not node.ready
    assert len(node.values) == 0
    assert node.device_config.manufacturer is None

    # the ready event contains a full (and complete) dump of the node, including values
    event = Event(
        "ready",
        {
            "event": "ready",
            "source": "node",
            "nodeId": node.node_id,
            "nodeState": multisensor_6_state,
            "result": [],
        },
    )
    node.receive_event(event)

    assert node.device_config.manufacturer == "AEON Labs"
    assert len(node.values) > 0

    new_state = deepcopy(multisensor_6_state)
    new_state["values"].append(
        {
            "commandClassName": "Binary Sensor",
            "commandClass": 48,
            "endpoint": 0,
            "property": "test",
            "propertyName": "test",
            "metadata": {
                "type": "boolean",
                "readable": True,
                "writeable": False,
                "label": "Any",
                "ccSpecific": {"sensorType": 255},
            },
            "value": False,
        }
    )
    new_state["endpoints"].append(
        {"nodeId": 52, "index": 1, "installerIcon": 3079, "userIcon": 3079}
    )

    event = Event(
        "ready",
        {
            "event": "ready",
            "source": "node",
            "nodeId": node.node_id,
            "nodeState": new_state,
            "result": [],
        },
    )
    node.receive_event(event)
    assert "52-48-0-test" in node.values
    assert 1 in node.endpoints

    new_state = deepcopy(new_state)
    new_state["endpoints"].pop(1)
    event = Event(
        "ready",
        {
            "event": "ready",
            "source": "node",
            "nodeId": node.node_id,
            "nodeState": multisensor_6_state,
            "result": [],
        },
    )
    node.receive_event(event)
    assert 1 not in node.endpoints


def test_node_ready_event(switch_enbrighten_zw3010_state):
    """Emulate a node ready event."""
    # when a node node is added, it has minimal info first
    node = node_pkg.Node(
        None, {"nodeId": 2, "status": 1, "ready": False, "values": [], "endpoints": []}
    )
    assert node.node_id == 2
    assert node.status == 1
    assert not node.ready
    assert len(node.values) == 0
    assert node.device_config.manufacturer is None

    # the ready event contains a full (and complete) dump of the node, including values
    event = Event(
        "ready",
        {
            "event": "ready",
            "source": "node",
            "nodeId": node.node_id,
            "nodeState": switch_enbrighten_zw3010_state,
            "result": [],
        },
    )
    # This will fail if the schema is invalid
    node.receive_event(event)

    assert len(node.values) > 0


async def test_node_status_events(multisensor_6):
    """Test Node status events."""
    node = multisensor_6
    assert node.status == NodeStatus.ASLEEP
    # mock node wake up event
    event = Event(type="wake up")
    node.handle_wake_up(event)
    assert node.status == NodeStatus.AWAKE
    # mock node dead event
    event = Event(type="dead")
    node.handle_dead(event)
    assert node.status == NodeStatus.DEAD
    # mock node alive event
    event = Event(type="alive")
    node.handle_alive(event)
    assert node.status == NodeStatus.ALIVE
    # mock node sleep event
    event = Event(type="sleep")
    node.handle_sleep(event)
    assert node.status == NodeStatus.ASLEEP


async def test_value_added_events(multisensor_6):
    """Test Node value added events for new value."""
    node = multisensor_6
    value_id = "52-112-0-6"
    # Validate that the value doesn't exist in the node state data
    assert value_id not in node.values
    event = Event(
        type="value added",
        data={
            "source": "node",
            "event": "value added",
            "nodeId": 52,
            "args": {
                "commandClassName": "Configuration",
                "commandClass": 112,
                "endpoint": 0,
                "property": 6,
                "propertyName": "Stay Awake in Battery Mode",
                "metadata": {
                    "type": "number",
                    "readable": True,
                    "writeable": True,
                    "valueSize": 1,
                    "min": 0,
                    "max": 1,
                    "default": 0,
                    "format": 0,
                    "allowManualEntry": False,
                    "states": {"0": "Disable", "1": "Enable"},
                    "label": "Stay Awake in Battery Mode",
                    "description": "Stay awake for 10 minutes at power on",
                    "isFromConfig": True,
                },
                "value": 0,
            },
        },
    )
    node.handle_value_added(event)
    assert isinstance(event.data["value"], ConfigurationValue)
    assert isinstance(node.values[value_id], ConfigurationValue)
    # ensure that the value was added to the node's state data
    assert value_id in node.values


async def test_value_updated_events(multisensor_6):
    """Test Node value updated events."""
    node = multisensor_6
    value_id = "52-112-0-2"
    # ensure that the value is in the node's state data
    assert value_id in node.values
    # assert the old value of the ZwaveValue
    assert (value_data := node.values[value_id].data) is not None
    assert value_data["value"] == node.values[value_id].value == 0
    event = Event(
        type="value updated",
        data={
            "source": "node",
            "event": "value updated",
            "nodeId": 52,
            "args": {
                "commandClassName": "Configuration",
                "commandClass": 112,
                "endpoint": 0,
                "property": 2,
                "propertyName": "Stay Awake in Battery Mode",
                "value": -1,
                "newValue": 1,
                "prevValue": 0,
            },
        },
    )
    node.handle_value_updated(event)
    assert isinstance(event.data["value"], ConfigurationValue)
    assert isinstance(node.values[value_id], ConfigurationValue)
    # ensure that the value is in to the node's state data
    assert value_id in node.values
    # ensure that the node's state data was updated and that old keys were removed
    assert (value_data := node.values[value_id].data) is not None
    assert value_data["metadata"]
    assert value_data["value"] == 1
    assert "newValue" not in value_data
    assert "prevValue" not in value_data
    # ensure that the value's state data was updated and that old keys were removed
    val = node.values[value_id]
    assert val.data["value"] == 1
    assert val.value == 1
    assert "newValue" not in val.data
    assert "prevValue" not in val.data


async def test_value_removed_events(multisensor_6):
    """Test Node value removed events."""
    node = multisensor_6
    value_id = "52-112-0-2"
    event = Event(
        type="value removed",
        data={
            "source": "node",
            "event": "value removed",
            "nodeId": 52,
            "args": {
                "commandClassName": "Configuration",
                "commandClass": 112,
                "endpoint": 0,
                "property": 2,
                "propertyName": "Stay Awake in Battery Mode",
                "prevValue": 0,
            },
        },
    )
    node.handle_value_removed(event)
    assert isinstance(event.data["value"], ConfigurationValue)
    # ensure that the value was removed from the nodes value's dict
    assert node.values.get(value_id) is None
    # ensure that the value was removed from the node's state data
    assert value_id not in node.values


async def test_value_notification(wallmote_central_scene: node_pkg.Node):
    """Test value notification events."""
    node = wallmote_central_scene

    # Validate that metadata gets added to notification when it's not included
    event = Event(
        type="value notification",
        data={
            "source": "node",
            "event": "value notification",
            "nodeId": 35,
            "args": {
                "commandClass": 91,
                "commandClassName": "Central Scene",
                "property": "scene",
                "propertyKey": "002",
                "propertyName": "scene",
                "propertyKeyName": "002",
                "ccVersion": 2,
                "value": 1,
            },
        },
    )

    node.handle_value_notification(event)
    assert event.data["value_notification"].metadata.states
    assert event.data["value_notification"].endpoint is not None
    assert event.data["value_notification"].value == 1
    # Let's make sure that the Value was not updated by the value notification event
    assert node.values["35-91-0-scene-002"].value is None

    # Validate that a value notification event for an unknown value gets returned as is
    event = Event(
        type="value notification",
        data={
            "source": "node",
            "event": "value notification",
            "nodeId": 35,
            "args": {
                "commandClass": 91,
                "commandClassName": "Central Scene",
                "property": "scene",
                "propertyKey": "005",
                "propertyName": "scene",
                "propertyKeyName": "005",
                "ccVersion": 2,
                "value": 2,
            },
        },
    )

    node.handle_value_notification(event)
    assert event.data["value_notification"].command_class == 91
    assert event.data["value_notification"].command_class_name == "Central Scene"
    assert event.data["value_notification"].property_ == "scene"
    assert event.data["value_notification"].property_name == "scene"
    assert event.data["value_notification"].property_key == "005"
    assert event.data["value_notification"].property_key_name == "005"
    assert event.data["value_notification"].value == 2


async def test_metadata_updated(climate_radio_thermostat_ct100_plus: node_pkg.Node):
    """Test metadata updated events."""
    node = climate_radio_thermostat_ct100_plus

    value = node.values["13-135-1-value"]

    assert not value.metadata.states

    # Validate that states becomes available on a value that doesn't have a state when
    # a metadata updated event with states is received
    event = Event(
        type="value notification",
        data={
            "source": "node",
            "event": "metadata updated",
            "nodeId": 13,
            "args": {
                "commandClassName": "Indicator",
                "commandClass": 135,
                "endpoint": 1,
                "property": "value",
                "propertyName": "value",
                "metadata": {
                    "type": "number",
                    "readable": True,
                    "writeable": True,
                    "min": 0,
                    "max": 255,
                    "label": "Indicator value",
                    "ccSpecific": {"indicatorId": 0},
                    "states": {
                        "0": "Idle",
                        "1": "Heating",
                        "2": "Cooling",
                        "3": "Fan Only",
                        "4": "Pending Heat",
                        "5": "Pending Cool",
                        "6": "Vent/Economizer",
                        "7": "Aux Heating",
                        "8": "2nd Stage Heating",
                        "9": "2nd Stage Cooling",
                        "10": "2nd Stage Aux Heat",
                        "11": "3rd Stage Aux Heat",
                    },
                },
                "value": 0,
            },
        },
    )

    node.handle_metadata_updated(event)
    assert value.metadata.states


async def test_notification(lock_schlage_be469: node_pkg.Node):
    """Test notification CC notification events."""
    node = lock_schlage_be469

    # Validate that Entry Control CC notification event is received as expected
    event = Event(
        type="notification",
        data={
            "source": "node",
            "event": "notification",
            "nodeId": 23,
            "ccId": 111,
            "endpointIndex": 0,
            "args": {
                "eventType": 0,
                "eventTypeLabel": "a",
                "dataType": 0,
                "dataTypeLabel": "b",
                "eventData": "test",
            },
        },
    )

    node.handle_notification(event)
    assert event.data["notification"].command_class == CommandClass.ENTRY_CONTROL
    assert event.data["notification"].node_id == 23
    assert event.data["notification"].endpoint_idx == 0
    assert event.data["notification"].event_type == EntryControlEventType.CACHING
    assert event.data["notification"].event_type_label == "a"
    assert event.data["notification"].data_type == EntryControlDataType.NONE
    assert event.data["notification"].data_type_label == "b"
    assert event.data["notification"].event_data == "test"

    # Validate that Notification CC notification event is received as expected
    event = Event(
        type="notification",
        data={
            "source": "node",
            "event": "notification",
            "nodeId": 23,
            "endpointIndex": 0,
            "ccId": 113,
            "args": {
                "type": 6,
                "event": 5,
                "label": "Access Control",
                "eventLabel": "Keypad lock operation",
                "parameters": {"userId": 1},
            },
        },
    )

    node.handle_notification(event)
    assert event.data["notification"].command_class == CommandClass.NOTIFICATION
    assert event.data["notification"].node_id == 23
    assert event.data["notification"].endpoint_idx == 0
    assert event.data["notification"].type_ == NotificationType.ACCESS_CONTROL
    assert (
        event.data["notification"].event
        == AccessControlNotificationEvent.KEYPAD_LOCK_OPERATION
    )
    assert event.data["notification"].label == "Access Control"
    assert event.data["notification"].event_label == "Keypad lock operation"
    assert event.data["notification"].parameters == {"userId": 1}

    # Validate that Power Level CC notification event is received as expected
    event = Event(
        type="notification",
        data={
            "source": "node",
            "event": "notification",
            "nodeId": 23,
            "endpointIndex": 0,
            "ccId": 115,
            "args": {"testNodeId": 1, "status": 0, "acknowledgedFrames": 2},
        },
    )

    node.handle_notification(event)
    assert event.data["notification"].command_class == CommandClass.POWERLEVEL
    assert event.data["notification"].node_id == 23
    assert event.data["notification"].endpoint_idx == 0
    assert event.data["notification"].test_node_id == 1
    assert event.data["notification"].status == PowerLevelTestStatus.FAILED
    assert event.data["notification"].acknowledged_frames == 2

    # Validate that Multilevel Switch CC notification event is received as expected
    event = Event(
        type="notification",
        data={
            "source": "node",
            "event": "notification",
            "nodeId": 23,
            "endpointIndex": 0,
            "ccId": 38,
            "args": {"direction": "up", "eventType": 4, "eventTypeLabel": "c"},
        },
    )

    node.handle_notification(event)
    assert event.data["notification"].command_class == CommandClass.SWITCH_MULTILEVEL
    assert event.data["notification"].node_id == 23
    assert event.data["notification"].endpoint_idx == 0
    assert event.data["notification"].direction == "up"
    assert (
        event.data["notification"].event_type
        == MultilevelSwitchCommand.START_LEVEL_CHANGE
    )
    assert event.data["notification"].event_type_label == "c"

    # Validate that Multilevel Switch CC notification event without a direction is valid
    event = Event(
        type="notification",
        data={
            "source": "node",
            "event": "notification",
            "nodeId": 23,
            "endpointIndex": 0,
            "ccId": 38,
            "args": {"eventType": 4, "eventTypeLabel": "c"},
        },
    )

    node.handle_notification(event)
    assert event.data["notification"].command_class == CommandClass.SWITCH_MULTILEVEL
    assert event.data["notification"].node_id == 23
    assert event.data["notification"].endpoint_idx == 0
    assert event.data["notification"].direction is None
    assert (
        event.data["notification"].event_type
        == MultilevelSwitchCommand.START_LEVEL_CHANGE
    )
    assert event.data["notification"].event_type_label == "c"

    # Validate that Battery CC notification event is received as expected
    event = Event(
        type="notification",
        data={
            "source": "node",
            "event": "notification",
            "nodeId": 23,
            "ccId": 128,
            "endpointIndex": 0,
            "args": {
                "eventType": "battery low",
                "urgency": 1,
            },
        },
    )

    node.handle_notification(event)
    assert event.data["notification"].command_class == CommandClass.BATTERY
    assert event.data["notification"].node_id == 23
    assert event.data["notification"].endpoint_idx == 0
    assert event.data["notification"].event_type == "battery low"
    assert event.data["notification"].urgency == BatteryReplacementStatus.SOON


async def test_notification_unknown(lock_schlage_be469: node_pkg.Node, caplog):
    """Test unrecognized command class notification events."""
    # Validate that an unrecognized CC notification event raises Exception
    node = lock_schlage_be469
    event = Event(
        type="notification",
        data={
            "source": "node",
            "event": "notification",
            "nodeId": 23,
            "ccId": 0,
        },
    )

    node.handle_notification(event)

    assert "notification" not in event.data


async def test_entry_control_notification(ring_keypad):
    """Test entry control CC notification events."""
    node = ring_keypad

    # Validate that Entry Control CC notification event is received as expected
    event = Event(
        type="notification",
        data={
            "source": "node",
            "event": "notification",
            "nodeId": 10,
            "endpointIndex": 0,
            "ccId": 111,
            "args": {
                "eventType": 5,
                "eventTypeLabel": "foo",
                "dataType": 2,
                "dataTypeLabel": "bar",
                "eventData": "cat",
            },
        },
    )
    node.handle_notification(event)
    assert event.data["notification"].command_class == CommandClass.ENTRY_CONTROL
    assert event.data["notification"].node_id == 10
    assert event.data["notification"].endpoint_idx == 0
    assert event.data["notification"].event_type == EntryControlEventType.ARM_AWAY
    assert event.data["notification"].event_type_label == "foo"
    assert event.data["notification"].data_type == EntryControlDataType.ASCII
    assert event.data["notification"].data_type_label == "bar"
    assert event.data["notification"].event_data == "cat"


async def test_interview_events(multisensor_6):
    """Test Node interview events."""
    node = multisensor_6
    assert node.interview_stage is None
    assert node.ready
    assert not node.in_interview

    event = Event(
        type="interview started",
        data={
            "source": "node",
            "event": "interview started",
            "nodeId": 52,
        },
    )
    node.handle_interview_started(event)
    assert node.interview_stage is None
    assert not node.ready
    assert not node.in_interview
    assert node.awaiting_manual_interview

    event = Event(
        type="interview stage completed",
        data={
            "source": "node",
            "event": "interview stage completed",
            "nodeId": 52,
            "stageName": "test",
        },
    )
    node.handle_interview_stage_completed(event)
    assert node.interview_stage == "test"
    assert not node.ready
    assert node.in_interview

    event = Event(
        type="interview failed",
        data={
            "source": "node",
            "event": "interview failed",
            "nodeId": 52,
        },
    )
    node.handle_interview_failed(event)
    assert node.interview_stage == INTERVIEW_FAILED
    assert not node.ready
    assert not node.in_interview

    event = Event(
        type="interview completed",
        data={
            "source": "node",
            "event": "interview completed",
            "nodeId": 52,
        },
    )
    node.handle_interview_completed(event)
    assert node.ready
    assert not node.in_interview


async def test_refresh_values(multisensor_6, uuid4, mock_command):
    """Test refresh_values and refresh_cc_values commands."""
    node: node_pkg.Node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.refresh_values", "nodeId": node.node_id},
        {"success": True},
    )
    await node.async_refresh_values()
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.refresh_values",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }

    ack_commands = mock_command(
        {
            "command": "node.refresh_cc_values",
            "nodeId": node.node_id,
            "commandClass": 112,
        },
        {"success": True},
    )
    await node.async_refresh_cc_values(CommandClass.CONFIGURATION)
    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "node.refresh_cc_values",
        "nodeId": node.node_id,
        "commandClass": 112,
        "messageId": uuid4,
    }


async def test_firmware_events(wallmote_central_scene: node_pkg.Node):
    """Test firmware events."""
    node = wallmote_central_scene
    assert node.firmware_update_progress is None

    event = Event(
        type="firmware update progress",
        data={
            "source": "node",
            "event": "firmware update progress",
            "nodeId": 35,
            "progress": {
                "currentFile": 1,
                "totalFiles": 1,
                "sentFragments": 1,
                "totalFragments": 10,
                "progress": 10.0,
            },
        },
    )

    node.handle_firmware_update_progress(event)
    progress = event.data["firmware_update_progress"]
    assert progress.current_file == 1
    assert progress.total_files == 1
    assert progress.sent_fragments == 1
    assert progress.total_fragments == 10
    assert progress.progress == 10.0
    assert node.firmware_update_progress
    assert node.firmware_update_progress.current_file == 1
    assert node.firmware_update_progress.total_files == 1
    assert node.firmware_update_progress.sent_fragments == 1
    assert node.firmware_update_progress.total_fragments == 10
    assert node.firmware_update_progress.progress == 10.0

    event = Event(
        type="firmware update finished",
        data={
            "source": "node",
            "event": "firmware update finished",
            "nodeId": 35,
            "result": {
                "status": 255,
                "success": True,
                "waitTime": 10,
                "reInterview": False,
            },
        },
    )

    node.handle_firmware_update_finished(event)
    result = event.data["firmware_update_finished"]
    assert result.status == NodeFirmwareUpdateStatus.OK_RESTART_PENDING
    assert result.success
    assert result.wait_time == 10
    assert not result.reinterview
    assert node.firmware_update_progress is None


async def test_value_added_value_exists(climate_radio_thermostat_ct100_plus):
    """Test value added event when value exists."""
    node: node_pkg.Node = climate_radio_thermostat_ct100_plus
    value_id = f"{node.node_id}-128-1-isHigh"
    value = node.values.get(value_id)
    assert value
    event = Event(
        "value added",
        {
            "source": "node",
            "event": "value added",
            "nodeId": node.node_id,
            "args": {
                "commandClassName": "Battery",
                "commandClass": 128,
                "endpoint": 1,
                "property": "isHigh",
                "propertyName": "isHigh",
                "metadata": {
                    "type": "boolean",
                    "readable": True,
                    "writeable": False,
                    "label": "High battery level",
                },
                "value": True,
            },
        },
    )
    node.receive_event(event)
    assert value_id in node.values
    assert node.values[value_id] is value


async def test_value_added_new_value(climate_radio_thermostat_ct100_plus):
    """Test value added event when new value is added."""
    node: node_pkg.Node = climate_radio_thermostat_ct100_plus
    event = Event(
        "value added",
        {
            "source": "node",
            "event": "value added",
            "nodeId": node.node_id,
            "args": {
                "commandClassName": "Battery",
                "commandClass": 128,
                "endpoint": 1,
                "property": "isMedium",
                "propertyName": "isMedium",
                "metadata": {
                    "type": "boolean",
                    "readable": True,
                    "writeable": False,
                    "label": "Medium battery level",
                },
                "value": True,
            },
        },
    )
    node.receive_event(event)
    assert f"{node.node_id}-128-1-isMedium" in node.values


async def test_invoke_cc_api(client, lock_schlage_be469, uuid4, mock_command):
    """Test endpoint.invoke_cc_api commands."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {"command": "endpoint.invoke_cc_api", "nodeId": node.node_id, "endpoint": 0},
        {"response": "ok"},
    )

    assert (
        await node.async_invoke_cc_api(CommandClass.USER_CODE, "set", 1, 1, "1234")
        == "ok"
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.invoke_cc_api",
        "nodeId": node.node_id,
        "endpoint": 0,
        "commandClass": 99,
        "methodName": "set",
        "args": [1, 1, "1234"],
        "messageId": uuid4,
    }

    assert (
        await node.async_invoke_cc_api(
            CommandClass.USER_CODE, "set", 2, 2, "1234", wait_for_result=True
        )
        == "ok"
    )

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "endpoint.invoke_cc_api",
        "nodeId": node.node_id,
        "endpoint": 0,
        "commandClass": 99,
        "methodName": "set",
        "args": [2, 2, "1234"],
        "messageId": uuid4,
    }

    with pytest.raises(NotFoundError):
        await node.async_invoke_cc_api(CommandClass.ANTITHEFT, "test", 1)


async def test_supports_cc_api(multisensor_6, uuid4, mock_command):
    """Test endpoint.supports_cc_api commands."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "endpoint.supports_cc_api", "nodeId": node.node_id, "endpoint": 0},
        {"supported": True},
    )

    assert await node.async_supports_cc_api(CommandClass.USER_CODE)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.supports_cc_api",
        "nodeId": node.node_id,
        "endpoint": 0,
        "commandClass": 99,
        "messageId": uuid4,
    }

    # Test that command fails when client is disconnected
    with patch("zwave_js_server.client.asyncio.Event.wait", return_value=True):
        await node.client.disconnect()

    with pytest.raises(FailedCommand):
        await node.async_supports_cc_api(CommandClass.USER_CODE)


async def test_supports_cc(multisensor_6, uuid4, mock_command):
    """Test endpoint.supports_cc_api commands."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "endpoint.supports_cc", "nodeId": node.node_id, "endpoint": 0},
        {"supported": True},
    )

    assert await node.async_supports_cc(CommandClass.USER_CODE)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.supports_cc",
        "nodeId": node.node_id,
        "endpoint": 0,
        "commandClass": 99,
        "messageId": uuid4,
    }

    # Test that command fails when client is disconnected
    with patch("zwave_js_server.client.asyncio.Event.wait", return_value=True):
        await node.client.disconnect()

    with pytest.raises(FailedCommand):
        await node.async_supports_cc(CommandClass.USER_CODE)


async def test_controls_cc(multisensor_6, uuid4, mock_command):
    """Test endpoint.controls_cc commands."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "endpoint.controls_cc", "nodeId": node.node_id, "endpoint": 0},
        {"controlled": True},
    )

    assert await node.async_controls_cc(CommandClass.USER_CODE)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.controls_cc",
        "nodeId": node.node_id,
        "endpoint": 0,
        "commandClass": 99,
        "messageId": uuid4,
    }

    # Test that command fails when client is disconnected
    with patch("zwave_js_server.client.asyncio.Event.wait", return_value=True):
        await node.client.disconnect()

    with pytest.raises(FailedCommand):
        await node.async_controls_cc(CommandClass.USER_CODE)


async def test_is_cc_secure(multisensor_6, uuid4, mock_command):
    """Test endpoint.is_cc_secure commands."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "endpoint.is_cc_secure", "nodeId": node.node_id, "endpoint": 0},
        {"secure": True},
    )

    assert await node.async_is_cc_secure(CommandClass.USER_CODE)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.is_cc_secure",
        "nodeId": node.node_id,
        "endpoint": 0,
        "commandClass": 99,
        "messageId": uuid4,
    }

    # Test that command fails when client is disconnected
    with patch("zwave_js_server.client.asyncio.Event.wait", return_value=True):
        await node.client.disconnect()

    with pytest.raises(FailedCommand):
        await node.async_is_cc_secure(CommandClass.USER_CODE)


async def test_get_cc_version(multisensor_6, uuid4, mock_command):
    """Test endpoint.get_cc_version commands."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "endpoint.get_cc_version", "nodeId": node.node_id, "endpoint": 0},
        {"version": 1},
    )

    assert await node.async_get_cc_version(CommandClass.USER_CODE) == 1

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.get_cc_version",
        "nodeId": node.node_id,
        "endpoint": 0,
        "commandClass": 99,
        "messageId": uuid4,
    }

    # Test that command fails when client is disconnected
    with patch("zwave_js_server.client.asyncio.Event.wait", return_value=True):
        await node.client.disconnect()

    with pytest.raises(FailedCommand):
        await node.async_get_cc_version(CommandClass.USER_CODE)


async def test_get_node_unsafe(multisensor_6, uuid4, mock_command):
    """Test endpoint.get_node_unsafe commands."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "endpoint.get_node_unsafe", "nodeId": node.node_id, "endpoint": 0},
        {"node": multisensor_6},
    )

    assert await node.async_get_node_unsafe() == multisensor_6

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.get_node_unsafe",
        "nodeId": node.node_id,
        "endpoint": 0,
        "messageId": uuid4,
    }

    # Test that command fails when client is disconnected
    with patch("zwave_js_server.client.asyncio.Event.wait", return_value=True):
        await node.client.disconnect()

    with pytest.raises(FailedCommand):
        await node.async_get_node_unsafe()


async def test_statistics_updated(
    wallmote_central_scene: node_pkg.Node, multisensor_6, ring_keypad
):
    """Test that statistics get updated on events."""
    node = wallmote_central_scene
    assert node.statistics.commands_rx == 0
    event = Event(
        "statistics updated",
        {
            "source": "node",
            "event": "statistics updated",
            "nodeId": node.node_id,
            "statistics": {
                "commandsTX": 1,
                "commandsRX": 2,
                "commandsDroppedTX": 3,
                "commandsDroppedRX": 4,
                "timeoutResponse": 5,
                "rtt": 6,
                "rssi": 7,
                "lwr": {
                    "protocolDataRate": 1,
                    "repeaters": [f"{wallmote_central_scene.node_id}"],
                    "repeaterRSSI": [1],
                    "routeFailedBetween": [
                        f"{ring_keypad.node_id}",
                        f"{multisensor_6.node_id}",
                    ],
                },
                "nlwr": {
                    "protocolDataRate": 2,
                    "repeaters": [],
                    "repeaterRSSI": [127],
                    "routeFailedBetween": [
                        f"{multisensor_6.node_id}",
                        f"{ring_keypad.node_id}",
                    ],
                },
            },
        },
    )
    node.receive_event(event)
    # Event should be modified with the NodeStatistics object
    assert "statistics_updated" in event.data
    event_stats: NodeStatistics = event.data["statistics_updated"]
    assert isinstance(event_stats, NodeStatistics)
    assert event_stats.commands_tx == 1
    assert event_stats.commands_rx == 2
    assert event_stats.commands_dropped_tx == 3
    assert event_stats.commands_dropped_rx == 4
    assert event_stats.timeout_response == 5
    assert event_stats.rtt == 6
    assert event_stats.rssi == 7
    assert event_stats.lwr
    assert event_stats.lwr.protocol_data_rate == ProtocolDataRate.ZWAVE_9K6
    assert event_stats.nlwr
    assert event_stats.nlwr.protocol_data_rate == ProtocolDataRate.ZWAVE_40K
    assert node.statistics == event_stats
    assert event_stats.lwr.as_dict() == {
        "protocol_data_rate": 1,
        "repeaters": [wallmote_central_scene],
        "repeater_rssi": [1],
        "rssi": None,
        "route_failed_between": (
            ring_keypad,
            multisensor_6,
        ),
    }

    statistics_data = {
        "commandsTX": 1,
        "commandsRX": 2,
        "commandsDroppedTX": 3,
        "commandsDroppedRX": 4,
        "timeoutResponse": 5,
    }
    assert node.data.get("statistics") != statistics_data
    event = Event(
        "statistics updated",
        {
            "source": "node",
            "event": "statistics updated",
            "nodeId": node.node_id,
            "statistics": statistics_data,
        },
    )
    node.receive_event(event)
    # Event should be modified with the NodeStatistics object
    assert "statistics_updated" in event.data
    event_stats: NodeStatistics = event.data["statistics_updated"]
    assert isinstance(event_stats, NodeStatistics)
    assert event_stats.commands_tx == 1
    assert event_stats.commands_rx == 2
    assert event_stats.commands_dropped_tx == 3
    assert event_stats.commands_dropped_rx == 4
    assert event_stats.timeout_response == 5
    assert not event_stats.rtt
    assert not event_stats.rssi
    assert not event_stats.lwr
    assert not event_stats.nlwr
    assert node.statistics == event_stats
    assert node.data["statistics"] == statistics_data

    # Test that invalid protocol data rate doesn't raise error
    event = Event(
        "statistics updated",
        {
            "source": "node",
            "event": "statistics updated",
            "nodeId": node.node_id,
            "statistics": {
                "commandsTX": 1,
                "commandsRX": 2,
                "commandsDroppedTX": 3,
                "commandsDroppedRX": 4,
                "timeoutResponse": 5,
                "rtt": 6,
                "rssi": 7,
                "lwr": {
                    "protocolDataRate": 0,
                    "repeaters": [],
                    "repeaterRSSI": [],
                    "routeFailedBetween": [],
                },
                "nlwr": {
                    "protocolDataRate": 0,
                    "repeaters": [],
                    "repeaterRSSI": [],
                    "routeFailedBetween": [],
                },
            },
        },
    )
    node.receive_event(event)
    # Event should be modified with the NodeStatistics object
    assert "statistics_updated" in event.data
    event_stats: NodeStatistics = event.data["statistics_updated"]
    assert isinstance(event_stats, NodeStatistics)
    assert not event_stats.lwr
    assert not event_stats.nlwr


async def test_statistics_updated_rssi_error(
    wallmote_central_scene: node_pkg.Node, multisensor_6, ring_keypad
):
    """Test that statistics get updated on events and rssi error is handled."""
    node = wallmote_central_scene
    assert node.statistics.commands_rx == 0
    event = Event(
        "statistics updated",
        {
            "source": "node",
            "event": "statistics updated",
            "nodeId": node.node_id,
            "statistics": {
                "commandsTX": 1,
                "commandsRX": 2,
                "commandsDroppedTX": 3,
                "commandsDroppedRX": 4,
                "timeoutResponse": 5,
                "rtt": 6,
                "rssi": 127,
                "lwr": {
                    "protocolDataRate": 1,
                    "repeaters": [f"{wallmote_central_scene.node_id}"],
                    "repeaterRSSI": [1],
                    "routeFailedBetween": [
                        f"{ring_keypad.node_id}",
                        f"{multisensor_6.node_id}",
                    ],
                },
                "nlwr": {
                    "protocolDataRate": 2,
                    "repeaters": [],
                    "repeaterRSSI": [127],
                    "routeFailedBetween": [
                        f"{multisensor_6.node_id}",
                        f"{ring_keypad.node_id}",
                    ],
                },
            },
        },
    )
    node.receive_event(event)
    # Event should be modified with the NodeStatistics object
    assert "statistics_updated" in event.data
    event_stats: NodeStatistics = event.data["statistics_updated"]
    assert isinstance(event_stats, NodeStatistics)
    with pytest.raises(RssiErrorReceived):
        assert event_stats.rssi


async def test_has_security_class(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test node.has_security_class command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.has_security_class", "nodeId": node.node_id},
        {"hasSecurityClass": True},
    )
    assert await node.async_has_security_class(SecurityClass.S2_AUTHENTICATED)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.has_security_class",
        "nodeId": node.node_id,
        "securityClass": SecurityClass.S2_AUTHENTICATED.value,
        "messageId": uuid4,
    }


async def test_has_security_class_undefined(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.has_security_class command response is undefined."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.has_security_class", "nodeId": node.node_id},
        {},
    )
    assert await node.async_has_security_class(SecurityClass.S2_AUTHENTICATED) is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.has_security_class",
        "nodeId": node.node_id,
        "securityClass": SecurityClass.S2_AUTHENTICATED.value,
        "messageId": uuid4,
    }


async def test_get_highest_security_class(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.get_highest_security_class command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.get_highest_security_class", "nodeId": node.node_id},
        {"highestSecurityClass": SecurityClass.S2_AUTHENTICATED.value},
    )
    assert (
        await node.async_get_highest_security_class() == SecurityClass.S2_AUTHENTICATED
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_highest_security_class",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_get_highest_security_class_undefined(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.get_highest_security_class command response is undefined."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.get_highest_security_class", "nodeId": node.node_id},
        {},
    )
    assert await node.async_get_highest_security_class() is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_highest_security_class",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_test_power_level(
    multisensor_6: node_pkg.Node,
    wallmote_central_scene: node_pkg.Node,
    uuid4,
    mock_command,
):
    """Test node.test_powerlevel command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.test_powerlevel", "nodeId": node.node_id},
        {"framesAcked": 1},
    )
    assert (
        await node.async_test_power_level(
            wallmote_central_scene, PowerLevel.DBM_MINUS_1, 3
        )
        == 1
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.test_powerlevel",
        "nodeId": node.node_id,
        "testNodeId": wallmote_central_scene.node_id,
        "powerlevel": PowerLevel.DBM_MINUS_1.value,
        "testFrameCount": 3,
        "messageId": uuid4,
    }


async def test_test_power_level_progress_event(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test test power level progress event."""
    event = Event(
        "test powerlevel progress",
        {
            "source": "node",
            "event": "test powerlevel progress",
            "nodeId": multisensor_6.node_id,
            "acknowledged": 1,
            "total": 2,
        },
    )
    multisensor_6.receive_event(event)
    assert event.data["test_power_level_progress"]
    assert event.data["test_power_level_progress"].acknowledged == 1
    assert event.data["test_power_level_progress"].total == 2


async def test_check_lifeline_health(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test node.check_lifeline_health command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.check_lifeline_health", "nodeId": node.node_id},
        {
            "summary": {
                "rating": 10,
                "results": [
                    LifelineHealthCheckResultDataType(
                        latency=1,
                        numNeighbors=2,
                        failedPingsNode=3,
                        rating=9,
                        routeChanges=4,
                        minPowerlevel=5,
                        failedPingsController=6,
                        snrMargin=7,
                    )
                ],
            }
        },
    )
    summary = await node.async_check_lifeline_health(1)

    assert summary.rating == 10
    assert summary.results[0].latency == 1
    assert summary.results[0].num_neighbors == 2
    assert summary.results[0].failed_pings_node == 3
    assert summary.results[0].rating == 9
    assert summary.results[0].route_changes == 4
    assert summary.results[0].min_power_level == PowerLevel.DBM_MINUS_5
    assert summary.results[0].failed_pings_controller == 6
    assert summary.results[0].snr_margin == 7

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.check_lifeline_health",
        "nodeId": node.node_id,
        "rounds": 1,
        "messageId": uuid4,
    }


async def test_check_lifeline_health_progress_event(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test check lifeline health progress event."""
    event = Event(
        "check lifeline health progress",
        {
            "source": "node",
            "event": "check lifeline health progress",
            "nodeId": multisensor_6.node_id,
            "rounds": 1,
            "totalRounds": 2,
            "lastRating": 10,
            "lastResult": LifelineHealthCheckResultDataType(
                latency=1,
                numNeighbors=2,
                failedPingsNode=3,
                rating=9,
                routeChanges=4,
                minPowerlevel=5,
                failedPingsController=6,
                snrMargin=7,
            ),
        },
    )
    multisensor_6.receive_event(event)
    assert event.data["check_lifeline_health_progress"]
    assert event.data["check_lifeline_health_progress"].rounds == 1
    assert event.data["check_lifeline_health_progress"].total_rounds == 2
    assert event.data["check_lifeline_health_progress"].last_rating == 10
    assert event.data["check_lifeline_health_progress"].last_result.latency == 1


async def test_check_route_health(
    multisensor_6: node_pkg.Node,
    wallmote_central_scene: node_pkg.Node,
    uuid4,
    mock_command,
):
    """Test node.check_route_health command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.check_route_health", "nodeId": node.node_id},
        {
            "summary": {
                "rating": 10,
                "results": [
                    RouteHealthCheckResultDataType(
                        numNeighbors=1,
                        rating=10,
                        failedPingsToSource=2,
                        failedPingsToTarget=3,
                        minPowerlevelSource=4,
                        minPowerlevelTarget=5,
                    )
                ],
            }
        },
    )
    summary = await node.async_check_route_health(wallmote_central_scene, 1)

    assert summary.rating == 10
    assert summary.results[0].num_neighbors == 1
    assert summary.results[0].rating == 10
    assert summary.results[0].failed_pings_to_source == 2
    assert summary.results[0].failed_pings_to_target == 3
    assert summary.results[0].min_power_level_source == PowerLevel.DBM_MINUS_4
    assert summary.results[0].min_power_level_target == PowerLevel.DBM_MINUS_5

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.check_route_health",
        "nodeId": node.node_id,
        "targetNodeId": wallmote_central_scene.node_id,
        "rounds": 1,
        "messageId": uuid4,
    }


async def test_check_route_health_progress_event(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test check route health progress event."""
    event = Event(
        "check route health progress",
        {
            "source": "node",
            "event": "check route health progress",
            "nodeId": multisensor_6.node_id,
            "rounds": 1,
            "totalRounds": 2,
            "lastRating": 10,
            "lastResult": RouteHealthCheckResultDataType(
                numNeighbors=1,
                rating=10,
                failedPingsToSource=2,
                failedPingsToTarget=3,
                minPowerlevelSource=4,
                minPowerlevelTarget=5,
            ),
        },
    )
    multisensor_6.receive_event(event)
    assert event.data["check_route_health_progress"]
    assert event.data["check_route_health_progress"].rounds == 1
    assert event.data["check_route_health_progress"].total_rounds == 2
    assert event.data["check_route_health_progress"].last_rating == 10
    assert event.data["check_route_health_progress"].last_result.num_neighbors == 1


async def test_get_state(
    multisensor_6: node_pkg.Node,
    multisensor_6_state: node_pkg.NodeDataType,
    uuid4,
    mock_command,
):
    """Test node.get_state command."""
    node = multisensor_6
    value_id = get_value_id_str(node, 32, "currentValue", 0)

    # Verify original values
    assert node.endpoints[0].installer_icon == 3079
    assert node.values[value_id].value == 255

    new_state = deepcopy(multisensor_6_state)
    # Update endpoint 0 installer icon
    new_state["endpoints"][0]["installerIcon"] = 1
    # Update value of {nodeId}-32-0-currentValue
    new_state["values"][0] = {
        "commandClassName": "Basic",
        "commandClass": 32,
        "endpoint": 0,
        "property": "currentValue",
        "propertyName": "currentValue",
        "metadata": {
            "type": "number",
            "readable": True,
            "writeable": False,
            "min": 0,
            "max": 99,
            "label": "Current value",
        },
        "value": 0,
    }
    ack_commands = mock_command(
        {"command": "node.get_state", "nodeId": node.node_id},
        {"state": new_state},
    )

    # Verify new values
    assert await node.async_get_state() == new_state
    # Verify original values are still the same
    assert node.endpoints[0].installer_icon != 1
    assert node.values[value_id].value != 0

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_state",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_update_endpoints(
    shelly_wave_shutter_state: node_pkg.NodeDataType,
    shelly_wave_shutter: node_pkg.Node,
) -> None:
    """Test updating endpoints of a node."""
    node = shelly_wave_shutter
    assert len(node.endpoints) == 3
    for endpoint_idx, endpoint in node.endpoints.items():
        assert endpoint.node_id == node.node_id
        assert endpoint.index == endpoint_idx
        for value in endpoint.values.values():
            assert value.node.node_id == node.node_id
            assert value.endpoint == endpoint_idx

    node_data = deepcopy(shelly_wave_shutter_state)
    new_endpoints = [
        endpoint_pkg.EndpointDataType(
            nodeId=node.node_id,
            index=0,
            commandClasses=[],
        ),
        endpoint_pkg.EndpointDataType(
            nodeId=node.node_id,
            index=1,
            commandClasses=[],
        ),
        endpoint_pkg.EndpointDataType(
            nodeId=node.node_id,
            index=3,
            commandClasses=[],
        ),
    ]
    node_data["endpoints"] = new_endpoints

    node.update(node_data)

    assert len(node.endpoints) == 3
    for endpoint_data in new_endpoints:
        assert endpoint_data["index"] in node.endpoints
        assert node.endpoints[endpoint_data["index"]].node_id == node.node_id
        assert node.endpoints[endpoint_data["index"]].index == endpoint_data["index"]
    for endpoint_idx, endpoint in node.endpoints.items():
        assert endpoint.node_id == node.node_id
        assert endpoint.index == endpoint_idx
        for value in endpoint.values.values():
            assert value.node.node_id == node.node_id
            assert value.endpoint == endpoint_idx


async def test_set_name(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test node.set_name command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.set_name", "nodeId": node.node_id},
        {},
    )

    assert node.name != "new_name"
    assert await node.async_set_name("new_name", False) is None
    assert node.name == "new_name"

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_name",
        "nodeId": node.node_id,
        "name": "new_name",
        "updateCC": False,
        "messageId": uuid4,
    }


async def test_set_location(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test node.set_location command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.set_location", "nodeId": node.node_id},
        {},
    )

    assert node.location != "new_location"
    assert await node.async_set_location("new_location", False) is None
    assert node.location == "new_location"

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_location",
        "nodeId": node.node_id,
        "location": "new_location",
        "updateCC": False,
        "messageId": uuid4,
    }


async def test_set_keep_awake(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test node.set_keep_awake command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.set_keep_awake", "nodeId": node.node_id},
        {},
    )

    assert node.keep_awake
    assert await node.async_set_keep_awake(False) is None
    assert node.keep_awake is False

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_keep_awake",
        "nodeId": node.node_id,
        "keepAwake": False,
        "messageId": uuid4,
    }


async def test_get_firmware_update_capabilities(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.get_firmware_update_capabilities command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.get_firmware_update_capabilities", "nodeId": node.node_id},
        {
            "capabilities": {
                "firmwareUpgradable": True,
                "firmwareTargets": [0],
                "continuesToFunction": True,
                "supportsActivation": True,
            }
        },
    )
    capabilities = await node.async_get_firmware_update_capabilities()
    assert capabilities.firmware_upgradable
    assert capabilities.firmware_targets == [0]
    assert capabilities.continues_to_function
    assert capabilities.supports_activation

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_firmware_update_capabilities",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }

    assert capabilities.to_dict() == {
        "firmware_upgradable": True,
        "firmware_targets": [0],
        "continues_to_function": True,
        "supports_activation": True,
    }


async def test_get_firmware_update_capabilities_false(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.get_firmware_update_capabilities cmd without firmware support."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.get_firmware_update_capabilities", "nodeId": node.node_id},
        {"capabilities": {"firmwareUpgradable": False}},
    )
    capabilities = await node.async_get_firmware_update_capabilities()
    assert not capabilities.firmware_upgradable
    with pytest.raises(TypeError):
        assert capabilities.firmware_targets
    with pytest.raises(TypeError):
        assert capabilities.continues_to_function
    with pytest.raises(TypeError):
        assert capabilities.supports_activation

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_firmware_update_capabilities",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }

    assert capabilities.to_dict() == {"firmware_upgradable": False}


async def test_get_firmware_update_capabilities_string(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.get_firmware_update_capabilities cmd without firmware support."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.get_firmware_update_capabilities", "nodeId": node.node_id},
        {
            "capabilities": {
                "firmwareUpgradable": True,
                "firmwareTargets": [0],
                "continuesToFunction": "unknown",
                "supportsActivation": "unknown",
            }
        },
    )
    capabilities = await node.async_get_firmware_update_capabilities()
    assert capabilities.firmware_upgradable
    assert capabilities.firmware_targets == [0]
    assert capabilities.continues_to_function is None
    assert capabilities.supports_activation is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_firmware_update_capabilities",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_get_firmware_update_capabilities_cached(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.get_firmware_update_capabilities_cached command."""
    node = multisensor_6
    ack_commands = mock_command(
        {
            "command": "node.get_firmware_update_capabilities_cached",
            "nodeId": node.node_id,
        },
        {
            "capabilities": {
                "firmwareUpgradable": True,
                "firmwareTargets": [0],
                "continuesToFunction": True,
                "supportsActivation": True,
            }
        },
    )
    capabilities = await node.async_get_firmware_update_capabilities_cached()
    assert capabilities.firmware_upgradable
    assert capabilities.firmware_targets == [0]
    assert capabilities.continues_to_function
    assert capabilities.supports_activation

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_firmware_update_capabilities_cached",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }

    assert capabilities.to_dict() == {
        "firmware_upgradable": True,
        "firmware_targets": [0],
        "continues_to_function": True,
        "supports_activation": True,
    }


async def test_is_firmware_update_in_progress(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.is_firmware_update_in_progress command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.is_firmware_update_in_progress", "nodeId": node.node_id},
        {"progress": True},
    )

    assert await node.async_is_firmware_update_in_progress()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.is_firmware_update_in_progress",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_interview(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test node.interview command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.interview", "nodeId": node.node_id},
        {},
    )

    await node.async_interview()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.interview",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_manually_idle_notification_value(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.manually_idle_notification_value command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.manually_idle_notification_value", "nodeId": node.node_id},
        {},
    )

    await node.async_manually_idle_notification_value(
        f"{node.node_id}-113-0-Home Security-Cover status"
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.manually_idle_notification_value",
        "nodeId": node.node_id,
        "valueId": {
            "commandClass": 113,
            "endpoint": 0,
            "property": "Home Security",
            "propertyKey": "Cover status",
        },
        "messageId": uuid4,
    }

    # Raise ValueError if the value is not for the right CommandClass
    with pytest.raises(ValueError):
        await node.async_manually_idle_notification_value(f"{node.node_id}-112-0-255")


async def test_set_date_and_time_no_wait(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.set_date_and_time command without waiting."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.set_date_and_time", "nodeId": node.node_id},
        {"success": True},
    )

    assert await node.async_set_date_and_time(datetime(2020, 1, 1, 12, 0, 0)) is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_date_and_time",
        "nodeId": node.node_id,
        "date": "2020-01-01T12:00:00",
        "messageId": uuid4,
    }


async def test_set_date_and_time(
    climate_radio_thermostat_ct100_plus: node_pkg.Node, uuid4, mock_command
):
    """Test node.set_date_and_time command while waiting for response."""
    node = climate_radio_thermostat_ct100_plus
    ack_commands = mock_command(
        {"command": "node.set_date_and_time", "nodeId": node.node_id},
        {"success": True},
    )

    assert await node.async_set_date_and_time(datetime(2020, 1, 1, 12, 0, 0))

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_date_and_time",
        "nodeId": node.node_id,
        "date": "2020-01-01T12:00:00",
        "messageId": uuid4,
    }


async def test_get_date_and_time(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test node.get_date_and_time command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.get_date_and_time", "nodeId": node.node_id},
        {"dateAndTime": {"hour": 1, "minute": 2, "weekday": 5}},
    )

    date_and_time = await node.async_get_date_and_time()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_date_and_time",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }
    assert date_and_time.hour == 1
    assert date_and_time.minute == 2
    assert date_and_time.weekday == Weekday.FRIDAY


async def test_get_value_timestamp(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test node.get_value_timestamp command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.get_value_timestamp", "nodeId": node.node_id},
        {"timestamp": 1234567890},
    )

    val = node.values["52-32-0-targetValue"]
    assert await node.async_get_value_timestamp(val) == 1234567890

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_value_timestamp",
        "nodeId": node.node_id,
        "valueId": {"commandClass": 32, "endpoint": 0, "property": "targetValue"},
        "messageId": uuid4,
    }

    assert await node.async_get_value_timestamp("52-112-0-2") == 1234567890

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "node.get_value_timestamp",
        "nodeId": node.node_id,
        "valueId": {"commandClass": 112, "endpoint": 0, "property": 2},
        "messageId": uuid4,
    }


async def test_is_health_check_in_progress(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test node.is_health_check_in_progress command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.is_health_check_in_progress", "nodeId": node.node_id},
        {"progress": True},
    )

    assert await node.async_is_health_check_in_progress()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.is_health_check_in_progress",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_abort_health_check(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test node.abort_health_check command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.abort_health_check", "nodeId": node.node_id},
        {},
    )

    await node.async_abort_health_check()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.abort_health_check",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_unknown_event(multisensor_6: node_pkg.Node, caplog):
    """Test that an unknown event type logs a message but does not raise."""
    caplog.set_level(logging.INFO)
    event = Event("unknown_event", {"source": "node", "event": "unknown_event"})
    multisensor_6.receive_event(event)
    assert len(caplog.records) == 1
    assert "Unhandled node event: unknown_event" in caplog.records[0].message
    assert caplog.records[0].levelno == logging.INFO


async def test_default_volume(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test default volume."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.set_default_volume", "nodeId": node.node_id},
        {},
    )
    assert node.default_volume is None
    await node.async_set_default_volume(10)
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_default_volume",
        "defaultVolume": 10,
        "nodeId": node.node_id,
        "messageId": uuid4,
    }
    assert node.default_volume == 10


async def test_default_transition_duration(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test default transition duration."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.set_default_transition_duration", "nodeId": node.node_id},
        {},
    )
    assert node.default_transition_duration is None
    await node.async_set_default_transition_duration(10)
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_default_transition_duration",
        "defaultTransitionDuration": 10,
        "nodeId": node.node_id,
        "messageId": uuid4,
    }
    assert node.default_transition_duration == 10


async def test_has_device_config_changed(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test has device config changed."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.has_device_config_changed", "nodeId": node.node_id},
        {"changed": True},
    )
    assert await node.async_has_device_config_changed()
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.has_device_config_changed",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_has_device_config_changed_undefined(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test has device config changed returns undefined."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.has_device_config_changed", "nodeId": node.node_id},
        {},
    )
    assert await node.async_has_device_config_changed() is None
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.has_device_config_changed",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


async def test_is_secure_none(client, multisensor_6_state):
    """Test is_secure when it's not included in the dump."""
    node_state = deepcopy(multisensor_6_state)
    node_state.pop("isSecure")
    node = node_pkg.Node(client, node_state)
    assert node.is_secure is None


async def test_set_raw_config_parameter_value(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test set raw config parameter value."""
    node = multisensor_6

    ack_commands = mock_command(
        {"command": "endpoint.set_raw_config_parameter_value", "nodeId": node.node_id},
        {},
    )

    result = await node.async_set_raw_config_parameter_value(1, 101, 1)
    assert result == SetConfigParameterResult(CommandStatus.QUEUED)

    assert len(ack_commands) == 1

    assert ack_commands[0] == {
        "command": "endpoint.set_raw_config_parameter_value",
        "nodeId": node.node_id,
        "endpoint": 0,
        "parameter": 101,
        "bitMask": 1,
        "value": 1,
        "messageId": uuid4,
    }

    result = await node.async_set_raw_config_parameter_value(2, 0)
    assert result == SetConfigParameterResult(CommandStatus.QUEUED)

    assert len(ack_commands) == 2

    assert ack_commands[1] == {
        "command": "endpoint.set_raw_config_parameter_value",
        "nodeId": node.node_id,
        "endpoint": 0,
        "parameter": 0,
        "value": 2,
        "messageId": uuid4,
    }

    # wake up node
    event = Event(
        "wake up", {"source": "node", "event": "wake up", "nodeId": node.node_id}
    )
    node.receive_event(event)

    result = await node.async_set_raw_config_parameter_value(
        1, 2, value_size=1, value_format=ConfigurationValueFormat.SIGNED_INTEGER
    )
    assert result == SetConfigParameterResult(CommandStatus.ACCEPTED)

    assert len(ack_commands) == 3

    assert ack_commands[2] == {
        "command": "endpoint.set_raw_config_parameter_value",
        "nodeId": node.node_id,
        "endpoint": 0,
        "parameter": 2,
        "valueSize": 1,
        "valueFormat": 0,
        "value": 1,
        "messageId": uuid4,
    }

    # Test failures
    with pytest.raises(ValueError):
        await node.async_set_raw_config_parameter_value(1, 101, 1, 1)

    with pytest.raises(ValueError):
        await node.async_set_raw_config_parameter_value(
            1, 101, 1, value_format=ConfigurationValueFormat.SIGNED_INTEGER
        )

    with pytest.raises(ValueError):
        await node.async_set_raw_config_parameter_value(
            1, 101, 1, 1, ConfigurationValueFormat.SIGNED_INTEGER
        )


async def test_get_raw_config_parameter_value(
    multisensor_6: node_pkg.Node, uuid4, mock_command
):
    """Test get raw config parameter value."""
    node = multisensor_6

    ack_commands = mock_command(
        {"command": "endpoint.get_raw_config_parameter_value", "nodeId": node.node_id},
        {"value": 1},
    )

    value = await node.async_get_raw_config_parameter_value(101)
    assert value == 1

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.get_raw_config_parameter_value",
        "nodeId": node.node_id,
        "endpoint": 0,
        "parameter": 101,
        "messageId": uuid4,
    }


async def test_supervision_result(inovelli_switch: node_pkg.Node, uuid4, mock_command):
    """Test Supervision Result."""
    node = inovelli_switch

    mock_command(
        {"command": "endpoint.set_raw_config_parameter_value", "nodeId": node.node_id},
        {"result": {"status": 1, "remainingDuration": "default"}},
    )

    result = await node.async_set_raw_config_parameter_value(1, 1)
    assert result.result.status is SupervisionStatus.WORKING
    duration = result.result.remaining_duration
    assert duration.unit == "default"


async def test_supervision_result_invalid(
    inovelli_switch: node_pkg.Node, uuid4, mock_command
):
    """Test invalid Supervision Result."""
    node = inovelli_switch

    mock_command(
        {"command": "endpoint.set_raw_config_parameter_value", "nodeId": node.node_id},
        {"result": {"status": 1}},
    )

    with pytest.raises(ValueError):
        await node.async_set_raw_config_parameter_value(1, 1)


async def test_node_info_received_event(multisensor_6: node_pkg.Node):
    """Test that the node info received event is successfully validated by pydantic."""
    node = multisensor_6
    event_type = "node info received"
    event_data = {"source": "node", "event": event_type, "nodeId": node.node_id}
    event = Event(event_type, event_data)

    def callback(data: dict) -> None:
        assert data == event_data

    node.on(event_type, callback)
    node.receive_event(event)
