"""Test the node model."""
from copy import deepcopy
import json
from unittest.mock import patch

import pytest

from zwave_js_server.const import (
    INTERVIEW_FAILED,
    CommandClass,
    NodeStatus,
    PowerLevel,
    ProtocolVersion,
    SecurityClass,
)
from zwave_js_server.const.command_class.entry_control import (
    EntryControlDataType,
    EntryControlEventType,
)
from zwave_js_server.event import Event
from zwave_js_server.exceptions import FailedCommand, NotFoundError, UnwriteableValue
from zwave_js_server.model import node as node_pkg
from zwave_js_server.model.firmware import FirmwareUpdateStatus
from zwave_js_server.model.node_health_check import (
    LifelineHealthCheckResultDataType,
    RouteHealthCheckResultDataType,
)
from zwave_js_server.model.node_statistics import NodeStatistics
from zwave_js_server.model.value import ConfigurationValue, get_value_id

from .. import load_fixture


def test_from_state():
    """Test from_state method."""
    state = json.loads(load_fixture("basic_dump.txt").split("\n")[0])["result"]["state"]

    node = node_pkg.Node(None, state["nodes"][0])

    assert node.node_id == 1
    assert node.index == 0
    assert node.status == 4
    assert node.ready is True
    assert node.device_class.basic.key == 2
    assert node.device_class.generic.label == "Static Controller"
    assert node.device_class.mandatory_supported_ccs == []
    assert node.device_class.mandatory_controlled_ccs == [32]

    assert node.is_listening is True
    assert node.is_frequent_listening is False
    assert node.is_routing is False
    assert node.max_data_rate == 100000
    assert node.supported_data_rates == [40000, 100000]
    assert node.is_secure is False
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


async def test_highest_security_value(lock_schlage_be469, ring_keypad):
    """Test the highest_security_class property"""
    assert lock_schlage_be469.highest_security_class == SecurityClass.S0_LEGACY
    assert ring_keypad.highest_security_class is None


async def test_device_config(wallmote_central_scene):
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
        "https://products.z-wavealliance.org/ProductManual/File?folder=&filename=MarketCertificationFiles/2479/ZP3111-5_R2_20170316.pdf"
    )
    assert device_config.metadata.wakeup is None
    assert device_config.associations == {}
    assert device_config.param_information == {"_map": {}}
    assert device_config.supports_zwave_plus is None


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
    value = node.values[value_id]
    assert await node.async_set_value(value_id, 42) is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": value.data,
        "value": 42,
        "messageId": uuid4,
    }

    # Set value with options
    assert await node.async_set_value(value_id, 42, {"transitionDuration": 1}) is None

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": value.data,
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


async def test_poll_value(multisensor_6, uuid4, mock_command):
    """Test poll value."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.poll_value", "nodeId": node.node_id},
        {"result": "something"},
    )
    value_id = "52-32-0-currentValue"
    value = node.values[value_id]
    assert await node.async_poll_value(value_id) is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.poll_value",
        "nodeId": node.node_id,
        "valueId": value.data,
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

    value_id = "52-32-0-targetValue"
    value = node.values[value_id]
    result = await node.async_get_value_metadata(value)

    assert result.type == "any"
    assert result.readable is True
    assert result.writeable is False
    assert result.label == "Node ID of the controller"
    assert result.description == "Description of the value metadata"

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_value_metadata",
        "nodeId": node.node_id,
        "valueId": value.data,
        "messageId": uuid4,
    }


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


def test_node_inclusion():
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
    state = json.loads(load_fixture("multisensor_6_state.json"))
    event = Event("ready", {"nodeState": state})
    node.receive_event(event)

    assert node.device_config.manufacturer == "AEON Labs"
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
    with pytest.raises(StopIteration):
        node.value_data_idx(value_id)
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
    assert node.value_data_idx(value_id)


async def test_value_updated_events(multisensor_6):
    """Test Node value updated events."""
    node = multisensor_6
    value_id = "52-112-0-2"
    # ensure that the value is in the node's state data
    assert (value_idx := node.value_data_idx(value_id))
    # assert the old value of the ZwaveValue
    assert (value_data := node.data["values"][value_idx]) is not None
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
                "newValue": 1,
                "prevValue": 0,
            },
        },
    )
    node.handle_value_updated(event)
    assert isinstance(event.data["value"], ConfigurationValue)
    assert isinstance(node.values[value_id], ConfigurationValue)
    # ensure that the value is in to the node's state data
    assert (value_idx := node.value_data_idx(value_id))
    # ensure that the node's state data was updated and that old keys were removed
    assert (value_data := node.data["values"][value_idx]) is not None
    assert value_data["metadata"]
    assert value_data["value"] == 1
    assert "newValue" not in value_data
    assert "prevValue" not in value_data
    # ensure that the value's state data was updated and that old keys were removed
    val = node.values[value_id]
    assert val.data["value"] == 1
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
    with pytest.raises(StopIteration):
        node.value_data_idx(value_id)


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

    # Validate that Notification CC notification event is received as expected
    event = Event(
        type="notification",
        data={
            "source": "node",
            "event": "notification",
            "nodeId": 23,
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
    assert event.data["notification"].type_ == 6
    assert event.data["notification"].event == 5
    assert event.data["notification"].label == "Access Control"
    assert event.data["notification"].event_label == "Keypad lock operation"
    assert event.data["notification"].parameters == {"userId": 1}


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
            "ccId": 111,
            "args": {"eventType": 5, "dataType": 2, "eventData": "555"},
        },
    )
    node.handle_notification(event)
    assert event.data["notification"].command_class == CommandClass.ENTRY_CONTROL
    assert event.data["notification"].node_id == 10
    assert event.data["notification"].event_type == EntryControlEventType.ARM_AWAY
    assert event.data["notification"].data_type == EntryControlDataType.ASCII
    assert event.data["notification"].event_data == "555"


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
    assert node.in_interview

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
            "sentFragments": 1,
            "totalFragments": 10,
        },
    )

    node.handle_firmware_update_progress(event)
    assert event.data["firmware_update_progress"].sent_fragments == 1
    assert event.data["firmware_update_progress"].total_fragments == 10
    assert node.firmware_update_progress
    assert node.firmware_update_progress.sent_fragments == 1
    assert node.firmware_update_progress.total_fragments == 10

    event = Event(
        type="firmware update finished",
        data={
            "source": "node",
            "event": "firmware update finished",
            "nodeId": 35,
            "status": 255,
            "waitTime": 10,
        },
    )

    node.handle_firmware_update_finished(event)
    assert (
        event.data["firmware_update_finished"].status
        == FirmwareUpdateStatus.OK_RESTART_PENDING
    )
    assert event.data["firmware_update_finished"].wait_time == 10
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


async def test_invoke_cc_api(multisensor_6, uuid4, mock_command):
    """Test endpoint. commands."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "endpoint.invoke_cc_api", "nodeId": node.node_id, "endpoint": 0},
        {"response": "ok"},
    )

    assert (
        await node.async_invoke_cc_api(CommandClass.USER_CODE, "set", 1, 1, "1234")
        is None
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


async def test_statistics_updated(wallmote_central_scene: node_pkg.Node):
    """Test that statistics get updated on events."""
    node = wallmote_central_scene
    assert node.statistics.commands_rx == 0
    event = Event(
        "statistics updated",
        {
            "source": "node",
            "event": "statistics updated",
            "statistics": {
                "commandsTX": 1,
                "commandsRX": 1,
                "commandsDroppedTX": 1,
                "commandsDroppedRX": 1,
                "timeoutResponse": 1,
            },
        },
    )
    node.receive_event(event)
    # Event should be modified with the NodeStatistics object
    assert "statistics_updated" in event.data
    event_stats = event.data["statistics_updated"]
    assert isinstance(event_stats, NodeStatistics)
    assert node.statistics.timeout_response == 1
    assert node.statistics == event_stats


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


async def test_test_power_level(multisensor_6: node_pkg.Node, uuid4, mock_command):
    """Test node.test_powerlevel command."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.test_powerlevel", "nodeId": node.node_id},
        {"framesAcked": 1},
    )
    assert await node.async_test_power_level(2, PowerLevel.DBM_MINUS_1, 3) == 1

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.test_powerlevel",
        "nodeId": node.node_id,
        "testNodeId": 2,
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
        },
    )
    multisensor_6.receive_event(event)
    assert event.data["check_lifeline_health_progress"]
    assert event.data["check_lifeline_health_progress"].rounds == 1
    assert event.data["check_lifeline_health_progress"].total_rounds == 2
    assert event.data["check_lifeline_health_progress"].last_rating == 10


async def test_check_route_health(multisensor_6: node_pkg.Node, uuid4, mock_command):
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
    summary = await node.async_check_route_health(15, 1)

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
        "targetNodeId": 15,
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
        },
    )
    multisensor_6.receive_event(event)
    assert event.data["check_route_health_progress"]
    assert event.data["check_route_health_progress"].rounds == 1
    assert event.data["check_route_health_progress"].total_rounds == 2
    assert event.data["check_route_health_progress"].last_rating == 10


async def test_get_state(
    multisensor_6: node_pkg.Node,
    multisensor_6_state: node_pkg.NodeDataType,
    uuid4,
    mock_command,
):
    """Test node.get_state command."""
    node = multisensor_6
    value_id = get_value_id(node, 32, "currentValue", 0)

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
    assert await node.async_get_state() is None
    assert node.endpoints[0].installer_icon == 1
    assert node.values[value_id].value == 0

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.get_state",
        "nodeId": node.node_id,
        "messageId": uuid4,
    }


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
