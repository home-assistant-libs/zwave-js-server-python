"""Test node utility functions."""
import pytest

from zwave_js_server.const import CommandClass
from zwave_js_server.exceptions import NotFoundError
from zwave_js_server.util.multicast import (
    async_multicast_endpoint_get_cc_version,
    async_multicast_endpoint_invoke_cc_api,
    async_multicast_endpoint_supports_cc,
    async_multicast_endpoint_supports_cc_api,
    async_multicast_get_endpoint_count,
    async_multicast_set_value,
)


async def test_endpoint_get_cc_version_multicast(
    climate_radio_thermostat_ct100_plus, inovelli_switch, client, uuid4, mock_command
):
    """Test multicast_group.get_cc_version command."""
    node1 = climate_radio_thermostat_ct100_plus
    node2 = inovelli_switch
    ack_commands = mock_command(
        {"command": "multicast_group.get_cc_version"},
        {"version": 1},
    )

    assert (
        await async_multicast_endpoint_get_cc_version(
            client, 1, CommandClass.ALARM, [node1, node2]
        )
        == 1
    )

    assert ack_commands[0] == {
        "command": "multicast_group.get_cc_version",
        "index": 1,
        "commandClass": 113,
        "nodeIDs": [node1.node_id, node2.node_id],
        "messageId": uuid4,
    }


async def test_endpoint_get_cc_version_broadcast(client, uuid4, mock_command):
    """Test broadcast_node.get_cc_version command."""
    ack_commands = mock_command(
        {"command": "broadcast_node.get_cc_version"},
        {"version": 1},
    )

    assert (
        await async_multicast_endpoint_get_cc_version(client, 1, CommandClass.ALARM)
        == 1
    )

    assert ack_commands[0] == {
        "command": "broadcast_node.get_cc_version",
        "index": 1,
        "commandClass": 113,
        "messageId": uuid4,
    }


async def test_endpoint_supports_cc_broadcast(client, uuid4, mock_command):
    """Test broadcast_node.supports_cc command."""
    ack_commands = mock_command(
        {"command": "broadcast_node.supports_cc"},
        {"supported": True},
    )

    assert await async_multicast_endpoint_supports_cc(client, 1, CommandClass.ALARM)

    assert ack_commands[0] == {
        "command": "broadcast_node.supports_cc",
        "index": 1,
        "commandClass": 113,
        "messageId": uuid4,
    }


async def test_endpoint_supports_cc_multicast(
    climate_radio_thermostat_ct100_plus, inovelli_switch, client, uuid4, mock_command
):
    """Test multicast_group.supports_cc command."""
    node1 = climate_radio_thermostat_ct100_plus
    node2 = inovelli_switch
    ack_commands = mock_command(
        {"command": "multicast_group.supports_cc"},
        {"supported": True},
    )

    assert await async_multicast_endpoint_supports_cc(
        client, 1, CommandClass.ALARM, [node1, node2]
    )

    assert ack_commands[0] == {
        "command": "multicast_group.supports_cc",
        "index": 1,
        "commandClass": 113,
        "nodeIDs": [node1.node_id, node2.node_id],
        "messageId": uuid4,
    }


async def test_get_endpoint_count_broadcast(client, uuid4, mock_command):
    """Test broadcast_node.get_endpoint_count command."""
    ack_commands = mock_command(
        {"command": "broadcast_node.get_endpoint_count"},
        {"count": 1},
    )

    assert await async_multicast_get_endpoint_count(client) == 1

    assert ack_commands[0] == {
        "command": "broadcast_node.get_endpoint_count",
        "messageId": uuid4,
    }


async def test_get_endpoint_count_multicast(
    climate_radio_thermostat_ct100_plus, inovelli_switch, client, uuid4, mock_command
):
    """Test multicast_group.get_endpoint_count command."""
    node1 = climate_radio_thermostat_ct100_plus
    node2 = inovelli_switch
    ack_commands = mock_command(
        {"command": "multicast_group.get_endpoint_count"},
        {"count": 1},
    )

    assert await async_multicast_get_endpoint_count(client, [node1, node2]) == 1

    assert ack_commands[0] == {
        "command": "multicast_group.get_endpoint_count",
        "nodeIDs": [node1.node_id, node2.node_id],
        "messageId": uuid4,
    }


async def test_set_value_broadcast(client, uuid4, mock_command):
    """Test broadcast_node.set_value command."""
    ack_commands = mock_command(
        {"command": "broadcast_node.set_value"},
        {"success": True},
    )

    assert await async_multicast_set_value(
        client, 1, {"commandClass": 1, "property": 1}
    )

    assert ack_commands[0] == {
        "command": "broadcast_node.set_value",
        "value": 1,
        "valueId": {"commandClass": 1, "property": 1},
        "options": None,
        "messageId": uuid4,
    }


async def test_set_value_multicast(
    climate_radio_thermostat_ct100_plus, inovelli_switch, client, uuid4, mock_command
):
    """Test multicast_group.set_value command."""
    node1 = climate_radio_thermostat_ct100_plus
    node2 = inovelli_switch
    ack_commands = mock_command(
        {"command": "multicast_group.set_value"},
        {"success": True},
    )

    assert await async_multicast_set_value(
        client, 1, {"commandClass": 112, "property": 1}, [node1, node2]
    )

    assert ack_commands[0] == {
        "command": "multicast_group.set_value",
        "nodeIDs": [node1.node_id, node2.node_id],
        "value": 1,
        "valueId": {"commandClass": 112, "property": 1},
        "options": None,
        "messageId": uuid4,
    }

    # Test invalid value
    with pytest.raises(NotFoundError):
        assert await async_multicast_set_value(
            client,
            1,
            {"commandClass": 1, "property": 1, "propertyKey": "invalid property key"},
            [node1, node2],
        )

    # Test invalid option
    with pytest.raises(NotFoundError):
        assert await async_multicast_set_value(
            client,
            1,
            {"commandClass": 112, "property": 1},
            nodes=[node1, node2],
            options={"test": 1},
        )


async def test_invoke_cc_api_broadcast(client, uuid4, mock_command):
    """Test broadcast_node.invoke_cc_api command."""
    ack_commands = mock_command(
        {"command": "broadcast_node.invoke_cc_api"},
        {"response": 1},
    )

    assert (
        await async_multicast_endpoint_invoke_cc_api(
            client, 1, 1, "test", ["test_args", "test_args2"]
        )
        == 1
    )

    assert ack_commands[0] == {
        "command": "broadcast_node.invoke_cc_api",
        "index": 1,
        "commandClass": 1,
        "methodName": "test",
        "args": ["test_args", "test_args2"],
        "messageId": uuid4,
    }


async def test_invoke_cc_api_multicast(
    climate_radio_thermostat_ct100_plus, inovelli_switch, client, uuid4, mock_command
):
    """Test multicast_group.invoke_cc_api command."""
    node1 = climate_radio_thermostat_ct100_plus
    node2 = inovelli_switch
    ack_commands = mock_command(
        {"command": "multicast_group.invoke_cc_api"},
        {"response": 1},
    )

    assert (
        await async_multicast_endpoint_invoke_cc_api(
            client, 1, 1, "test", ["test_args", "test_args2"], [node1, node2]
        )
        == 1
    )

    assert ack_commands[0] == {
        "command": "multicast_group.invoke_cc_api",
        "nodeIDs": [node1.node_id, node2.node_id],
        "index": 1,
        "commandClass": 1,
        "methodName": "test",
        "args": ["test_args", "test_args2"],
        "messageId": uuid4,
    }


async def test_supports_cc_api_broadcast(client, uuid4, mock_command):
    """Test broadcast_node.supports_cc_api command."""
    ack_commands = mock_command(
        {"command": "broadcast_node.supports_cc_api"},
        {"supported": True},
    )

    assert await async_multicast_endpoint_supports_cc_api(client, 1, 1)

    assert ack_commands[0] == {
        "command": "broadcast_node.supports_cc_api",
        "index": 1,
        "commandClass": 1,
        "messageId": uuid4,
    }


async def test_supports_cc_api_multicast(
    climate_radio_thermostat_ct100_plus, inovelli_switch, client, uuid4, mock_command
):
    """Test multicast_group.supports_cc_api command."""
    node1 = climate_radio_thermostat_ct100_plus
    node2 = inovelli_switch
    ack_commands = mock_command(
        {"command": "multicast_group.supports_cc_api"},
        {"supported": True},
    )

    assert await async_multicast_endpoint_supports_cc_api(client, 1, 1, [node1, node2])

    assert ack_commands[0] == {
        "command": "multicast_group.supports_cc_api",
        "nodeIDs": [node1.node_id, node2.node_id],
        "index": 1,
        "commandClass": 1,
        "messageId": uuid4,
    }
