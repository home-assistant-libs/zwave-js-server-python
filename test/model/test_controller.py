"""Test the controller model."""
import json
from zwave_js_server.model import association as association_pkg
from zwave_js_server.model import controller as controller_pkg

from .. import load_fixture


def test_from_state():
    """Test from_state method."""
    state = json.loads(load_fixture("basic_dump.txt").split("\n")[0])["result"]["state"]

    ctrl = controller_pkg.Controller(None, state)

    assert ctrl.library_version == "Z-Wave 3.95"
    assert ctrl.controller_type == 1
    assert ctrl.home_id == 3601639587
    assert ctrl.own_node_id == 1
    assert ctrl.is_secondary is False
    assert ctrl.is_using_home_id_from_other_network is False
    assert ctrl.is_SIS_present is True
    assert ctrl.was_real_primary is True
    assert ctrl.is_static_update_controller is True
    assert ctrl.is_slave is False
    assert ctrl.serial_api_version == "1.0"
    assert ctrl.manufacturer_id == 134
    assert ctrl.product_type == 257
    assert ctrl.product_id == 90
    assert ctrl.supported_function_types == [
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        28,
        32,
        33,
        34,
        35,
        36,
        39,
        41,
        42,
        43,
        44,
        45,
        65,
        66,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        80,
        81,
        83,
        84,
        85,
        86,
        87,
        94,
        96,
        97,
        98,
        99,
        102,
        103,
        128,
        144,
        146,
        147,
        152,
        180,
        182,
        183,
        184,
        185,
        186,
        189,
        190,
        191,
        210,
        211,
        212,
        238,
        239,
    ]
    assert ctrl.suc_node_id == 1
    assert ctrl.supports_timers is False


async def test_begin_inclusion(controller, uuid4, mock_command):
    """Test begin inclusion."""
    ack_commands = mock_command(
        {"command": "controller.begin_inclusion"},
        {"success": True},
    )
    assert await controller.async_begin_inclusion()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_inclusion",
        "includeNonSecure": None,
        "messageId": uuid4,
    }


async def test_stop_inclusion(controller, uuid4, mock_command):
    """Test stop inclusion."""
    ack_commands = mock_command(
        {"command": "controller.stop_inclusion"},
        {"success": True},
    )
    assert await controller.async_stop_inclusion()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.stop_inclusion",
        "messageId": uuid4,
    }


async def test_begin_exclusion(controller, uuid4, mock_command):
    """Test begin exclusion."""
    ack_commands = mock_command(
        {"command": "controller.begin_exclusion"},
        {"success": True},
    )
    assert await controller.async_begin_exclusion()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_exclusion",
        "messageId": uuid4,
    }


async def test_stop_exclusion(controller, uuid4, mock_command):
    """Test stop exclusion."""
    ack_commands = mock_command(
        {"command": "controller.stop_exclusion"},
        {"success": True},
    )
    assert await controller.async_stop_exclusion()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.stop_exclusion",
        "messageId": uuid4,
    }


async def test_hash(controller):
    """Test node hash."""
    assert hash(controller) == hash(controller.home_id)


async def test_remove_failed_node(controller, uuid4, mock_command):
    """Test remove failed node."""
    ack_commands = mock_command(
        {"command": "controller.remove_failed_node"},
        {},
    )

    node_id = 52
    assert await controller.async_remove_failed_node(node_id) is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.remove_failed_node",
        "messageId": uuid4,
        "nodeId": node_id,
    }


async def test_replace_failed_node(controller, uuid4, mock_command):
    """Test replace failed node."""
    ack_commands = mock_command(
        {"command": "controller.replace_failed_node"},
        {"success": True},
    )

    node_id = 52
    include_non_secure = True
    assert await controller.async_replace_failed_node(node_id, include_non_secure)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.replace_failed_node",
        "messageId": uuid4,
        "nodeId": node_id,
        "includeNonSecure": include_non_secure,
    }


async def test_heal_node(controller, uuid4, mock_command):
    """Test heal node."""
    ack_commands = mock_command(
        {"command": "controller.heal_node"},
        {"success": True},
    )

    node_id = 52
    assert await controller.async_heal_node(node_id)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.heal_node",
        "messageId": uuid4,
        "nodeId": node_id,
    }


async def test_begin_healing_network(controller, uuid4, mock_command):
    """Test begin healing network."""
    ack_commands = mock_command(
        {"command": "controller.begin_healing_network"},
        {"success": True},
    )

    assert await controller.async_begin_healing_network()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_healing_network",
        "messageId": uuid4,
    }


async def test_stop_healing_network(controller, uuid4, mock_command):
    """Test stop healing network."""
    ack_commands = mock_command(
        {"command": "controller.stop_healing_network"},
        {"success": True},
    )

    assert await controller.async_stop_healing_network()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.stop_healing_network",
        "messageId": uuid4,
    }


async def test_is_failed_node(controller, uuid4, mock_command):
    """Test is failed node."""
    ack_commands = mock_command(
        {"command": "controller.is_failed_node"},
        {"failed": False},
    )

    node_id = 52
    assert await controller.async_is_failed_node(node_id) is False

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.is_failed_node",
        "messageId": uuid4,
        "nodeId": node_id,
    }


async def test_get_association_groups(controller, uuid4, mock_command):
    """Test get association groups."""

    issued_commands = {2: [37, 43, 43], 5: [50, 114]}

    ack_commands = mock_command(
        {"command": "controller.get_association_groups"},
        {
            "groups": {
                1: {
                    "maxNodes": 10,
                    "isLifeline": True,
                    "multiChannel": True,
                    "label": "Association Group 1",
                },
                2: {
                    "maxNodes": 30,
                    "isLifeline": False,
                    "multiChannel": False,
                    "label": "Association Group 2",
                    "profile": 2,
                    "issuedCommands": issued_commands,
                },
            }
        },
    )

    node_id = 52
    result = await controller.async_get_association_groups(node_id)

    assert result[1].max_nodes == 10
    assert result[1].is_lifeline is True
    assert result[1].multi_channel is True
    assert result[1].label == "Association Group 1"
    assert result[1].profile is None
    assert result[1].issued_commands == {}

    assert result[2].max_nodes == 30
    assert result[2].is_lifeline is False
    assert result[2].multi_channel is False
    assert result[2].label == "Association Group 2"
    assert result[2].profile == 2
    for attr, value in issued_commands.items():
        assert result[2].issued_commands[attr] == value

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_association_groups",
        "messageId": uuid4,
        "nodeId": node_id,
    }


async def test_get_associations(controller, uuid4, mock_command):
    """Test get associations."""

    ack_commands = mock_command(
        {"command": "controller.get_associations"},
        {
            "associations": {
                1: {
                    "nodeId": 10,
                },
                2: {
                    "nodeId": 30,
                    "endpoint": 0,
                },
            }
        },
    )

    node_id = 52
    result = await controller.async_get_associations(node_id)

    assert result[1].node_id == 10
    assert result[1].endpoint is None

    assert result[2].node_id == 30
    assert result[2].endpoint == 0

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_associations",
        "messageId": uuid4,
        "nodeId": node_id,
    }


async def test_is_association_allowed(controller, uuid4, mock_command):
    """Test is association allowed."""

    ack_commands = mock_command(
        {"command": "controller.is_association_allowed"},
        {"allowed": True},
    )

    node_id = 52
    group = 0
    association = association_pkg.Association(node_id=5, endpoint=0)

    assert await controller.async_is_association_allowed(node_id, group, association)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.is_association_allowed",
        "messageId": uuid4,
        "nodeId": node_id,
        "group": group,
        "association": {"nodeId": 5, "endpoint": 0},
    }


async def test_add_associations(controller, uuid4, mock_command):
    """Test add associations."""

    ack_commands = mock_command(
        {"command": "controller.add_associations"},
        {},
    )

    node_id = 52
    group = 0
    associations = [
        association_pkg.Association(node_id=5, endpoint=0),
        association_pkg.Association(node_id=10),
    ]

    await controller.async_add_associations(node_id, group, associations)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.add_associations",
        "messageId": uuid4,
        "nodeId": node_id,
        "group": group,
        "associations": [
            {"nodeId": 5, "endpoint": 0},
            {"nodeId": 10, "endpoint": None},
        ],
    }


async def test_remove_associations(controller, uuid4, mock_command):
    """Test remove associations."""

    ack_commands = mock_command(
        {"command": "controller.remove_associations"},
        {},
    )

    node_id = 52
    group = 0
    associations = [
        association_pkg.Association(node_id=5, endpoint=0),
        association_pkg.Association(node_id=10),
    ]

    await controller.async_remove_associations(node_id, group, associations)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.remove_associations",
        "messageId": uuid4,
        "nodeId": node_id,
        "group": group,
        "associations": [
            {"nodeId": 5, "endpoint": 0},
            {"nodeId": 10, "endpoint": None},
        ],
    }


async def test_remove_node_from_all_associations(controller, uuid4, mock_command):
    """Test remove associations."""

    ack_commands = mock_command(
        {"command": "controller.remove_node_from_all_associations"},
        {},
    )

    node_id = 52
    await controller.async_remove_node_from_all_associations(node_id)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.remove_node_from_all_associations",
        "messageId": uuid4,
        "nodeId": node_id,
    }


async def test_get_node_neighbors(controller, uuid4, mock_command):
    """Test get node neighbors."""

    ack_commands = mock_command({"command": "controller.get_node_neighbors"}, {"neighbors": [1, 2]})

    node_id = 52
    assert await controller.async_get_node_neighbors(node_id) == [1, 2]

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_node_neighbors",
        "messageId": uuid4,
        "nodeId": node_id,
    }
