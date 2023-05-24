"""Test node utility functions."""
import copy
from unittest.mock import patch

import pytest

from zwave_js_server.const import CommandClass, CommandStatus
from zwave_js_server.exceptions import (
    BulkSetConfigParameterFailed,
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


@pytest.mark.parametrize("endpoint", [0, 1])
async def test_configuration_parameter_values(
    endpoint,
    client,
    climate_radio_thermostat_ct100_plus_state,
    inovelli_switch_state,
    uuid4,
    mock_command,
):
    """Test node methods to get and set configuration parameter values."""
    node_state = copy.deepcopy(climate_radio_thermostat_ct100_plus_state)
    node_2_state = copy.deepcopy(inovelli_switch_state)
    # Put all config parameters on endpoint we are testing
    for state in (node_state, node_2_state):
        for value in state["values"]:
            if (
                value["commandClass"] == CommandClass.CONFIGURATION
                and value["endpoint"] == 0
            ):
                value["endpoint"] = endpoint

    node: Node = Node(client, node_state)
    node_2: Node = Node(client, node_2_state)
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
        await async_set_config_parameter(node, 1, 2, endpoint=endpoint)

    # Test setting a manual entry configuration parameter with an invalid value
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node_2, "Purple", 8, 255, endpoint=endpoint)

    # Test setting a manual entry configuration parameter with a valid value
    ack_commands_2 = mock_command(
        {"command": "node.set_value", "nodeId": node_2.node_id},
        {"success": True},
    )

    zwave_value, cmd_status = await async_set_config_parameter(
        node_2, 190, 8, 255, endpoint=endpoint
    )
    assert isinstance(zwave_value, ConfigurationValue)
    assert cmd_status == CommandStatus.ACCEPTED

    value = node_2.values[f"31-112-{endpoint}-8-255"]
    assert len(ack_commands_2) == 1
    assert ack_commands_2[0] == {
        "command": "node.set_value",
        "nodeId": node_2.node_id,
        "valueId": {
            "commandClass": 112,
            "endpoint": endpoint,
            "property": 8,
            "propertyKey": 255,
        },
        "value": 190,
        "messageId": uuid4,
    }

    zwave_value, cmd_status = await async_set_config_parameter(
        node_2, "Blue", 8, 255, endpoint=endpoint
    )
    assert isinstance(zwave_value, ConfigurationValue)
    assert cmd_status == CommandStatus.ACCEPTED

    value = node_2.values[f"31-112-{endpoint}-8-255"]
    assert len(ack_commands_2) == 2
    assert ack_commands_2[1] == {
        "command": "node.set_value",
        "nodeId": node_2.node_id,
        "valueId": {
            "commandClass": 112,
            "endpoint": endpoint,
            "property": 8,
            "propertyKey": 255,
        },
        "value": 170,
        "messageId": uuid4,
    }

    # Test setting an enumerated configuration parameter with an invalid value
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node, 5, 1, endpoint=endpoint)

    # Test setting a range configuration parameter with an out of bounds value
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node, 200, 10, endpoint=endpoint)

    # Test configuration parameter not found when using an invalid property name
    with pytest.raises(NotFoundError):
        await async_set_config_parameter(
            node, 5, "fake configuration parameter name", endpoint=endpoint
        )

    # Test using an invalid state label to set a value
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node, "fake state label", 1, endpoint=endpoint)

    # Test configuration parameter not found when property key is invalid
    with pytest.raises(NotFoundError):
        await async_set_config_parameter(node, 1, 1, property_key=1, endpoint=endpoint)

    # Test setting a configuration parameter by state label and property name
    zwave_value, cmd_status = await async_set_config_parameter(
        node, "2.0\u00b0 F", "Temperature Reporting Threshold", endpoint=endpoint
    )
    assert isinstance(zwave_value, ConfigurationValue)
    assert cmd_status == CommandStatus.ACCEPTED

    value = node.values[f"13-112-{endpoint}-1"]
    assert len(ack_commands) == 3
    assert ack_commands[2] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {
            "commandClass": 112,
            "endpoint": endpoint,
            "property": 1,
        },
        "value": 4,
        "messageId": uuid4,
    }


@pytest.mark.parametrize("endpoint", [0, 1])
async def test_bulk_set_partial_config_parameters(
    endpoint, client, multisensor_6_state, uuid4, mock_command
):
    """Test bulk setting partial config parameters."""
    node_state = copy.deepcopy(multisensor_6_state)
    # Put all config parameters on endpoint we are testing
    for value in node_state["values"]:
        if (
            value["commandClass"] == CommandClass.CONFIGURATION
            and value["endpoint"] == 0
        ):
            value["endpoint"] = endpoint
    node: Node = Node(client, node_state)
    ack_commands = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": True},
    )
    cmd_status = await async_bulk_set_partial_config_parameters(
        node, 101, 241, endpoint=endpoint
    )
    assert cmd_status == CommandStatus.QUEUED
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {
            "commandClass": CommandClass.CONFIGURATION.value,
            "endpoint": endpoint,
            "property": 101,
        },
        "value": 241,
        "messageId": uuid4,
    }

    cmd_status = await async_bulk_set_partial_config_parameters(
        node, 101, {128: 1, 64: 1, 32: 1, 16: 1, 1: 1}, endpoint=endpoint
    )
    assert cmd_status == CommandStatus.QUEUED
    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {
            "commandClass": CommandClass.CONFIGURATION.value,
            "endpoint": endpoint,
            "property": 101,
        },
        "value": 241,
        "messageId": uuid4,
    }

    # Only set some values so we use cached values for the rest
    cmd_status = await async_bulk_set_partial_config_parameters(
        node, 101, {64: 1, 32: 1, 16: 1, 1: 1}, endpoint=endpoint
    )
    assert cmd_status == CommandStatus.QUEUED
    assert len(ack_commands) == 3
    assert ack_commands[2] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {
            "commandClass": CommandClass.CONFIGURATION.value,
            "endpoint": endpoint,
            "property": 101,
        },
        "value": 241,
        "messageId": uuid4,
    }

    # Use property key names instead of bitmasks for dict key
    cmd_status = await async_bulk_set_partial_config_parameters(
        node,
        101,
        {
            "Group 1: Send humidity reports": 1,
            "Group 1: Send temperature reports": 1,
            "Group 1: Send ultraviolet reports": 1,
            "Group 1: Send battery reports": 1,
        },
        endpoint=endpoint,
    )
    assert cmd_status == CommandStatus.QUEUED
    assert len(ack_commands) == 4
    assert ack_commands[3] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {
            "commandClass": CommandClass.CONFIGURATION.value,
            "endpoint": endpoint,
            "property": 101,
        },
        "value": 241,
        "messageId": uuid4,
    }

    # Use an invalid property
    with pytest.raises(NotFoundError):
        await async_bulk_set_partial_config_parameters(node, 999, 99, endpoint=endpoint)

    # use an invalid bitmask
    with pytest.raises(NotFoundError):
        await async_bulk_set_partial_config_parameters(
            node, 101, {128: 1, 64: 1, 32: 1, 16: 1, 2: 1}, endpoint=endpoint
        )

    # use an invalid property name
    with pytest.raises(NotFoundError):
        await async_bulk_set_partial_config_parameters(
            node, 101, {"Invalid property name": 1}, endpoint=endpoint
        )

    # use an invalid bitmask
    with pytest.raises(BulkSetConfigParameterFailed):
        await async_bulk_set_partial_config_parameters(
            node, 101, {128: 1, 64: 1, 32: 1, 16: 1, 1: 99999}, endpoint=endpoint
        )

    # Try to bulkset a property that isn't broken into partials with a dictionary
    with pytest.raises(ValueTypeError):
        await async_bulk_set_partial_config_parameters(
            node, 252, {1: 1}, endpoint=endpoint
        )

    # Try to bulkset a property that isn't broken into partials, it should fall back to
    # async_set_config_parameter
    with patch("zwave_js_server.util.node.async_set_config_parameter") as mock_cmd:
        mock_cmd.return_value = (None, None)
        await async_bulk_set_partial_config_parameters(node, 252, 1, endpoint=endpoint)
        mock_cmd.assert_called_once()


@pytest.mark.parametrize("endpoint", [0, 1])
async def test_bulk_set_with_full_and_partial_parameters(
    endpoint, client, partial_and_full_parameter_state, uuid4, mock_command
):
    """Test bulk setting config parameters when state has full and partial values."""
    node_state = copy.deepcopy(partial_and_full_parameter_state)
    # Put all config parameters on endpoint we are testing
    for value in node_state["values"]:
        if (
            value["commandClass"] == CommandClass.CONFIGURATION
            and value["endpoint"] == 0
        ):
            value["endpoint"] = endpoint
    node: Node = Node(client, node_state)
    ack_commands = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": True},
    )

    cmd_status = await async_bulk_set_partial_config_parameters(
        node, 8, 34867929, endpoint=endpoint
    )

    assert cmd_status == CommandStatus.ACCEPTED
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": {
            "commandClass": CommandClass.CONFIGURATION.value,
            "endpoint": endpoint,
            "property": 8,
        },
        "value": 34867929,
        "messageId": uuid4,
    }


@pytest.mark.parametrize("endpoint", [0, 1])
async def test_failures(endpoint, client, multisensor_6_state, mock_command):
    """Test setting config parameter failures."""
    node_state = copy.deepcopy(multisensor_6_state)
    # Put all config parameters on endpoint we are testing
    for value in node_state["values"]:
        if (
            value["commandClass"] == CommandClass.CONFIGURATION
            and value["endpoint"] == 0
        ):
            value["endpoint"] = endpoint
    node: Node = Node(client, node_state)
    # We need the node to be alive so we wait for a response
    node.handle_alive(node)

    mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": False},
    )

    with pytest.raises(SetValueFailed):
        await async_bulk_set_partial_config_parameters(
            node, 101, {64: 1, 32: 1, 16: 1, 1: 1}, endpoint=endpoint
        )

    with pytest.raises(SetValueFailed):
        await async_set_config_parameter(node, 1, 101, 64, endpoint=endpoint)


@pytest.mark.parametrize("endpoint", [0, 1])
async def test_returned_values(endpoint, client, multisensor_6_state, mock_command):
    """Test returned values from setting config parameters."""
    node_state = copy.deepcopy(multisensor_6_state)
    # Put all config parameters on endpoint we are testing
    for value in node_state["values"]:
        if (
            value["commandClass"] == CommandClass.CONFIGURATION
            and value["endpoint"] == 0
        ):
            value["endpoint"] = endpoint
    node: Node = Node(client, node_state)
    # We need the node to be alive so we wait for a response
    node.handle_alive(node)

    mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": True},
    )

    cmd_status = await async_bulk_set_partial_config_parameters(
        node, 101, {64: 1, 32: 1, 16: 1, 1: 1}, endpoint=endpoint
    )
    assert cmd_status == CommandStatus.ACCEPTED

    zwave_value, cmd_status = await async_set_config_parameter(
        node, 1, 101, 64, endpoint=endpoint
    )
    assert isinstance(zwave_value, ConfigurationValue)
    assert cmd_status == CommandStatus.ACCEPTED
