"""Test lock utility functions."""
import copy

import pytest

from zwave_js_server.const import SupervisionStatus
from zwave_js_server.const.command_class.lock import (
    ATTR_CODE_SLOT,
    ATTR_IN_USE,
    ATTR_NAME,
    ATTR_USERCODE,
    DoorLockCCConfigurationSetOptions,
    OperationType,
)
from zwave_js_server.exceptions import NotFoundError
from zwave_js_server.model.node import Node
from zwave_js_server.model.value import SupervisionResult
from zwave_js_server.util.lock import (
    clear_usercode,
    get_code_slots,
    get_usercode,
    get_usercode_from_node,
    get_usercodes,
    set_configuration,
    set_usercode,
)

from .const import CODE_SLOTS


def test_get_code_slots(lock_schlage_be469):
    """Test get_code_slots utility function."""
    node = lock_schlage_be469
    assert get_code_slots(node) == [
        {k: v for k, v in code_slot.items() if k != ATTR_USERCODE}
        for code_slot in CODE_SLOTS
    ]


def test_get_usercode(lock_schlage_be469):
    """Test get_usercode utility function."""
    node = lock_schlage_be469

    # Test in use slot
    slot = get_usercode(node, 1)
    assert all(char == "*" for char in slot[ATTR_USERCODE])

    # Test unused slot
    assert get_usercode(node, 29)[ATTR_USERCODE] == ""

    # Test unknown slot
    assert get_usercode(node, 30)[ATTR_USERCODE] is None

    # Test invalid slot
    with pytest.raises(NotFoundError):
        get_usercode(node, 100)


def test_get_usercodes(lock_schlage_be469):
    """Test get_usercodes utility function."""
    node = lock_schlage_be469
    assert get_usercodes(node) == CODE_SLOTS


async def test_set_usercode(lock_schlage_be469, mock_command, uuid4):
    """Test set_usercode utility function."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"result": {"status": 255}},
    )

    # Test valid code
    await set_usercode(node, 1, "1234")
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_value",
        "nodeId": 20,
        "messageId": uuid4,
        "valueId": {
            "commandClass": 99,
            "endpoint": 0,
            "property": "userCode",
            "propertyKey": 1,
        },
        "value": "1234",
    }

    # Test invalid code slot
    with pytest.raises(NotFoundError):
        await set_usercode(node, 100, "1234")

    # assert no new command calls
    assert len(ack_commands) == 1

    # Test invalid code length
    with pytest.raises(ValueError):
        await set_usercode(node, 1, "123")

    # assert no new command calls
    assert len(ack_commands) == 1


async def test_clear_usercode(lock_schlage_be469, mock_command, uuid4):
    """Test clear_usercode utility function."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {"command": "node.set_value", "nodeId": node.node_id},
        {"result": {"status": 255}},
    )

    # Test valid code
    await clear_usercode(node, 1)
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_value",
        "nodeId": 20,
        "messageId": uuid4,
        "valueId": {
            "commandClass": 99,
            "endpoint": 0,
            "property": "userIdStatus",
            "propertyKey": 1,
        },
        "value": 0,
    }

    # Test invalid code slot
    with pytest.raises(NotFoundError):
        await clear_usercode(node, 100)

    # assert no new command calls
    assert len(ack_commands) == 1


async def test_get_usercode_from_node(lock_schlage_be469, mock_command, uuid4):
    """Test get_usercode_from_node utility function."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {"command": "endpoint.invoke_cc_api", "nodeId": node.node_id, "endpoint": 0},
        {"response": {"userIdStatus": 1, "userCode": "**********"}},
    )

    # Test valid code
    assert await get_usercode_from_node(node, 1) == {
        ATTR_NAME: "User Code (1)",
        ATTR_CODE_SLOT: 1,
        ATTR_IN_USE: True,
        ATTR_USERCODE: "**********",
    }
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.invoke_cc_api",
        "nodeId": 20,
        "endpoint": 0,
        "commandClass": 99,
        "messageId": uuid4,
        "methodName": "get",
        "args": [1],
    }


async def test_set_configuration_empty_response(
    driver, lock_schlage_be469_state, mock_command, uuid4
):
    """Test set_configuration utility function without response."""
    node = Node(driver.client, copy.deepcopy(lock_schlage_be469_state))
    driver.controller.nodes[node.node_id] = node
    ack_commands = mock_command(
        {"command": "endpoint.invoke_cc_api", "nodeId": node.node_id, "endpoint": 0},
        {},
    )
    await set_configuration(
        node.endpoints[0],
        DoorLockCCConfigurationSetOptions(OperationType.CONSTANT),
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.invoke_cc_api",
        "nodeId": 20,
        "endpoint": 0,
        "commandClass": 98,
        "messageId": uuid4,
        "methodName": "setConfiguration",
        "args": [
            {
                "insideHandlesCanOpenDoorConfiguration": [True, True, True, True],
                "operationType": 1,
                "outsideHandlesCanOpenDoorConfiguration": [True, True, True, True],
            }
        ],
    }

    with pytest.raises(ValueError):
        await set_configuration(
            node.endpoints[0],
            DoorLockCCConfigurationSetOptions(OperationType.CONSTANT, 1),
        )

    with pytest.raises(ValueError):
        await set_configuration(
            node.endpoints[0],
            DoorLockCCConfigurationSetOptions(OperationType.TIMED),
        )


async def test_set_configuration_with_response(
    driver, lock_schlage_be469_state, mock_command, uuid4
):
    """Test set_configuration utility function with response."""
    node = Node(driver.client, copy.deepcopy(lock_schlage_be469_state))
    driver.controller.nodes[node.node_id] = node
    ack_commands = mock_command(
        {"command": "endpoint.invoke_cc_api", "nodeId": node.node_id, "endpoint": 0},
        {"response": {"status": 0}},
    )
    assert await set_configuration(
        node.endpoints[0],
        DoorLockCCConfigurationSetOptions(OperationType.CONSTANT),
    ) == SupervisionResult(SupervisionStatus.NO_SUPPORT)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "endpoint.invoke_cc_api",
        "nodeId": 20,
        "endpoint": 0,
        "commandClass": 98,
        "messageId": uuid4,
        "methodName": "setConfiguration",
        "args": [
            {
                "insideHandlesCanOpenDoorConfiguration": [True, True, True, True],
                "operationType": 1,
                "outsideHandlesCanOpenDoorConfiguration": [True, True, True, True],
            }
        ],
    }
