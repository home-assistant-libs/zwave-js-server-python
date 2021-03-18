"""Test the node model."""
import json

import pytest

from zwave_js_server.const import CommandClass
from zwave_js_server.event import Event
from zwave_js_server.exceptions import UnwriteableValue
from zwave_js_server.model import node as node_pkg
from zwave_js_server.model.node import Node, NodeStatus

from .. import load_fixture

DEVICE_CONFIG_FIXTURE = {
    "manufacturer_id": 134,
    "manufacturer": "AEON Labs",
    "label": "ZW090",
    "description": "Z‐Stick Gen5 USB Controller",
    "devices": [
        {"productType": 1, "productId": 90},
        {"productType": 257, "productId": 90},
        {"productType": 513, "productId": 90},
    ],
    "firmware_version": {"min": "0.0", "max": "255.255"},
    "associations": {},
    "param_information": {"_map": {}},
}


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
    assert node.max_data_rate == 40000
    assert node.is_secure is False
    assert node.protocol_version == 4
    assert node.supports_beaming is None
    assert node.manufacturer_id == 134
    assert node.product_id == 90
    assert node.product_type == 257
    for attr, value in DEVICE_CONFIG_FIXTURE.items():
        assert getattr(node.device_config, attr) == value
    assert node.label == "ZW090"
    assert node.neighbors == [23, 26, 5, 6]
    assert node.interview_attempts == 0
    assert len(node.endpoints) == 1
    assert node.endpoints[0].index == 0


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
        None, {"nodeId": 52, "status": 1, "ready": False, "values": []}
    )
    assert node.node_id == 52
    assert node.status == 1
    assert not node.ready
    assert len(node.values) == 0
    # the ready event contains a full (and complete) dump of the node, including values
    state = json.loads(load_fixture("multisensor_6_state.json"))
    event = Event("ready", {"nodeState": state})
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


async def test_value_notification(wallmote_central_scene: Node):
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


async def test_metadata_updated(climate_radio_thermostat_ct100_plus: Node):
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


async def test_notification(lock_schlage_be469: Node):
    """Test notification events."""
    node = lock_schlage_be469

    # Validate that metadata gets added to notification when it's not included
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
    assert event.data["notification"].type_ == 6
    assert event.data["notification"].event == 5
    assert event.data["notification"].label == "Access Control"
    assert event.data["notification"].event_label == "Keypad lock operation"
    assert event.data["notification"].parameters == {"userId": 1}
