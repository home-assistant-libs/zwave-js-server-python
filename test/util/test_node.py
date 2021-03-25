"""Test node utility functions."""
import pytest

from zwave_js_server.const import CommandClass, CommandStatus
from zwave_js_server.exceptions import (
    InvalidNewValue,
    NotFoundError,
    SetValueFailed,
    ValueTypeError,
)
from zwave_js_server.model.node import Node
from zwave_js_server.model.value import ConfigurationValue
from zwave_js_server.util.node import (
    async_bulk_set_partial_config_parameters,
    async_set_config_parameter,
)


async def test_configuration_parameter_values(
    climate_radio_thermostat_ct100_plus, inovelli_switch, uuid4, mock_command
):
    """Test node methods to get and set configuration parameter values."""
    node: Node = climate_radio_thermostat_ct100_plus
    node_2: Node = inovelli_switch
    ack_commands = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": True},
    )

    assert node.node_id == 13
    config_values = node.get_configuration_values()
    assert len(config_values) == 12

    assert node_2.node_id == 31
    config_values_2 = node_2.get_configuration_values()
    assert len(config_values_2) == 15

    for value in config_values.values():
        assert isinstance(value, ConfigurationValue)

    # Test setting a configuration parameter that has no metadata
    with pytest.raises(NotImplementedError):
        await async_set_config_parameter(node, 1, 2)

    # Test setting a manual entry configuration parameter with an invalid value
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node_2, "Purple", 8, 255)

    # Test setting a manual entry configuration parameter with a valid value
    ack_commands_2 = mock_command(
        {"command": "node.set_value", "nodeId": node_2.node_id},
        {"success": True},
    )

    zwave_value, cmd_status = await async_set_config_parameter(node_2, 190, 8, 255)
    assert isinstance(zwave_value, ConfigurationValue)
    assert cmd_status == CommandStatus.ACCEPTED

    value = node_2.values["31-112-0-8-255"]
    assert len(ack_commands_2) == 1
    assert ack_commands_2[0] == {
        "command": "node.set_value",
        "nodeId": node_2.node_id,
        "valueId": value.data,
        "value": 190,
        "messageId": uuid4,
    }

    zwave_value, cmd_status = await async_set_config_parameter(node_2, "Blue", 8, 255)
    assert isinstance(zwave_value, ConfigurationValue)
    assert cmd_status == CommandStatus.ACCEPTED

    value = node_2.values["31-112-0-8-255"]
    assert len(ack_commands_2) == 2
    assert ack_commands_2[1] == {
        "command": "node.set_value",
        "nodeId": node_2.node_id,
        "valueId": value.data,
        "value": 170,
        "messageId": uuid4,
    }

    # Test setting an enumerated configuration parameter with an invalid value
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node, 5, 1)

    # Test setting a range configuration parameter with an out of bounds value
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node, 200, 10)

    # Test configuration parameter not found when using an invalid property name
    with pytest.raises(NotFoundError):
        await async_set_config_parameter(node, 5, "fake configuration parameter name")

    # Test using an invalid state label to set a value
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node, "fake state label", 1)

    # Test configuration parameter not found when property key is invalid
    with pytest.raises(NotFoundError):
        await async_set_config_parameter(node, 1, 1, property_key=1)

    # Test setting a configuration parameter by state label and property name
    zwave_value, cmd_status = await async_set_config_parameter(
        node, "2.0\u00b0 F", "Temperature Reporting Threshold"
    )
    assert isinstance(zwave_value, ConfigurationValue)
    assert cmd_status == CommandStatus.ACCEPTED

    value = node.values["13-112-0-1"]
    assert len(ack_commands) == 3
    assert ack_commands[2] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": value.data,
        "value": 4,
        "messageId": uuid4,
    }


async def test_bulk_set_partial_config_parameters(multisensor_6, uuid4, mock_command):
    """Test bulk setting partial config parameters."""
    node: Node = multisensor_6
    ack_commands = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": True},
    )
    cmd_status = await async_bulk_set_partial_config_parameters(node, 101, 241)
    assert cmd_status == CommandStatus.QUEUED
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {
            "commandClass": CommandClass.CONFIGURATION.value,
            "property": 101,
        },
        "value": 241,
        "messageId": uuid4,
    }

    cmd_status = await async_bulk_set_partial_config_parameters(
        node, 101, {128: 1, 64: 1, 32: 1, 16: 1, 1: 1}
    )
    assert cmd_status == CommandStatus.QUEUED
    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {
            "commandClass": CommandClass.CONFIGURATION.value,
            "property": 101,
        },
        "value": 241,
        "messageId": uuid4,
    }

    # Only set some values so we use cached values for the rest
    cmd_status = await async_bulk_set_partial_config_parameters(
        node, 101, {64: 1, 32: 1, 16: 1, 1: 1}
    )
    assert cmd_status == CommandStatus.QUEUED
    assert len(ack_commands) == 3
    assert ack_commands[2] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {
            "commandClass": CommandClass.CONFIGURATION.value,
            "property": 101,
        },
        "value": 241,
        "messageId": uuid4,
    }

    # Use an invalid property
    with pytest.raises(NotFoundError):
        await async_bulk_set_partial_config_parameters(node, 999, 99)

    # use an invalid bitmask
    with pytest.raises(NotFoundError):
        await async_bulk_set_partial_config_parameters(
            node, 101, {128: 1, 64: 1, 32: 1, 16: 1, 2: 1}
        )

    # Try to bulkset a property that isn't broken into partials
    with pytest.raises(ValueTypeError):
        await async_bulk_set_partial_config_parameters(node, 252, 1)


async def test_failures(multisensor_6, mock_command):
    """Test setting config parameter failures."""
    node: Node = multisensor_6
    # We need the node to be alive so we wait for a response
    node.handle_alive(node)

    _ = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": False},
    )

    with pytest.raises(SetValueFailed):
        await async_bulk_set_partial_config_parameters(
            node, 101, {64: 1, 32: 1, 16: 1, 1: 1}
        )

    with pytest.raises(SetValueFailed):
        await async_set_config_parameter(node, 1, 101, 64)


async def test_returned_values(multisensor_6, mock_command):
    """Test returned values from setting config parameters."""
    node: Node = multisensor_6
    # We need the node to be alive so we wait for a response
    node.handle_alive(node)

    _ = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": True},
    )

    cmd_status = await async_bulk_set_partial_config_parameters(
        node, 101, {64: 1, 32: 1, 16: 1, 1: 1}
    )
    assert cmd_status == CommandStatus.ACCEPTED

    zwave_value, cmd_status = await async_set_config_parameter(node, 1, 101, 64)
    assert isinstance(zwave_value, ConfigurationValue)
    assert cmd_status == CommandStatus.ACCEPTED
