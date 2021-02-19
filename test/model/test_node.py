"""Test the node model."""
import json

import pytest

from zwave_js_server.model.value import ConfigurationValue
from zwave_js_server.const import CommandClass
from zwave_js_server.exceptions import InvalidNewValue, UnwriteableValue
from zwave_js_server.model import node as node_pkg
from zwave_js_server.event import Event

from .. import load_fixture

DEVICE_CLASS_FIXTURE = {
    "basic": "Routing Slave",
    "generic": "Static Controller",
    "specific": "PC Controller",
    "mandatory_supported_ccs": [],
    "mandatory_controlled_ccs": ["Basic"],
}

DEVICE_CONFIG_FIXTURE = {
    "manufacturer_id": 134,
    "manufacturer": "AEON Labs",
    "label": "ZW090",
    "description": "Z‐Stick Gen5 USB Controller",
    "devices": [
        {"productType": "0x0001", "productId": "0x005a"},
        {"productType": "0x0101", "productId": "0x005a"},
        {"productType": "0x0201", "productId": "0x005a"},
    ],
    "firmware_version": {"min": "0.0", "max": "255.255"},
    "associations": {},
    "param_information": {"_map": {}},
}


def test_from_state():
    """Test from_state method."""
    state = json.loads(load_fixture("basic_dump.txt").split("\n")[0])["state"]

    node = node_pkg.Node(None, state["nodes"][0])

    assert node.node_id == 1
    assert node.index == 0
    assert node.status == 4
    assert node.ready is True
    for attr, value in DEVICE_CLASS_FIXTURE.items():
        assert getattr(node.device_class, attr) == value

    assert node.is_listening is True
    assert node.is_frequent_listening is False
    assert node.is_routing is False
    assert node.max_baud_rate == 40000
    assert node.is_secure is False
    assert node.version == 4
    assert node.is_beaming is True
    assert node.manufacturer_id == 134
    assert node.product_id == 90
    assert node.product_type == 257
    for attr, value in DEVICE_CONFIG_FIXTURE.items():
        assert getattr(node.device_config, attr) == value
    assert node.label == "ZW090"
    assert node.neighbors == [31, 32, 33, 36, 37, 39, 52]
    assert node.interview_attempts == 1
    assert len(node.endpoints) == 1
    assert node.endpoints[0].index == 0


async def test_values_without_property_key_name(multisensor_6):
    """Test that values with property key and without property key name can be found."""
    node = multisensor_6
    assert "52-112-00-101-1-00" in node.values
    assert "52-112-00-101-16-00" in node.values


async def test_command_class_values(climate_radio_thermostat_ct100_plus):
    """Test node methods to get command class values."""
    node = climate_radio_thermostat_ct100_plus
    assert node.node_id == 13
    switch_values = node.get_command_class_values(CommandClass.SENSOR_MULTILEVEL)
    assert len(switch_values) == 2
    config_values = node.get_configuration_values()
    assert len(config_values) == 12

    for value in config_values.values():
        assert isinstance(value, ConfigurationValue)

    with pytest.raises(UnwriteableValue):
        await node.async_set_value("13-112-00-2-00-00", 1)

    with pytest.raises(InvalidNewValue):
        await node.async_set_value("13-112-00-1-00-00", 5)

    with pytest.raises(InvalidNewValue):
        await node.async_set_value("13-112-00-10-00-00", 200)


async def test_set_value(multisensor_6, uuid4, mock_command):
    """Test set value."""
    node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": True},
    )
    value_id = "52-32-00-targetValue-00-00"
    value = node.values[value_id]
    assert await node.async_set_value(value_id, 42)

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
    value_id = "52-32-00-currentValue-00-00"
    value = node.values[value_id]
    result = await node.async_poll_value(value_id)
    assert result == "something"

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

    value_id = "52-32-00-targetValue-00-00"
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
