"""Test node utility functions."""
import pytest

from zwave_js_server.exceptions import InvalidNewValue, NotFoundError
from zwave_js_server.model.node import Node
from zwave_js_server.model.value import ConfigurationValue
from zwave_js_server.util.node import async_set_config_parameter


async def test_configuration_parameter_values(
    climate_radio_thermostat_ct100_plus, uuid4, mock_command
):
    """Test node methods to get and set configuration parameter values."""
    node: Node = climate_radio_thermostat_ct100_plus
    ack_commands = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"success": True},
    )

    assert node.node_id == 13
    config_values = node.get_configuration_values()
    assert len(config_values) == 12

    for value in config_values.values():
        assert isinstance(value, ConfigurationValue)

    # Test setting a configuration parameter that has no metadata
    with pytest.raises(NotImplementedError):
        await async_set_config_parameter(node, 1, 2)

    # Test setting an enumerated configuration parameter with an invalid value
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node, 5, 1)

    # Test setting a range configuration parameter with an out of bounds value
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node, 200, 10)

    # Test configuration parameter not found when using an invalid property name
    with pytest.raises(NotFoundError):
        await async_set_config_parameter(node, 5, "fake configuration parameter name")

    # Test configuration parameter not found when using an invalid state label
    with pytest.raises(InvalidNewValue):
        await async_set_config_parameter(node, "fake state label", 1)

    # Test configuration parameter not found when property key is invalid
    with pytest.raises(NotFoundError):
        await async_set_config_parameter(node, 1, 1, property_key=1)

    # Test setting a configuration parameter by state label and property name
    await async_set_config_parameter(
        node, "2.0\u00b0 F", "Temperature Reporting Threshold"
    )

    value = node.values["13-112-00-1-00"]
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": value.data,
        "value": 4,
        "messageId": uuid4,
    }