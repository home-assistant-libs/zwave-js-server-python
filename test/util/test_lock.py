"""Test lock utility functions."""
import pytest

from zwave_js_server.const import ATTR_USERCODE
from zwave_js_server.exceptions import NotFoundError
from zwave_js_server.util.lock import (
    get_code_slots,
    get_usercode,
    get_usercodes,
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
    user_code = get_usercode(node, 1)
    assert all(char == "*" for char in user_code)

    # Test unused slot
    assert get_usercode(node, 30) is None

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
        {"success": True},
    )

    # Test valid code
    await set_usercode(node, 1, "1234")
    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.set_value",
        "nodeId": 20,
        "messageId": uuid4,
        "valueId": {
            "commandClassName": "User Code",
            "commandClass": 99,
            "endpoint": 0,
            "property": "userCode",
            "propertyName": "userCode",
            "propertyKey": 1,
            "propertyKeyName": "1",
            "metadata": {
                "type": "string",
                "readable": True,
                "writeable": True,
                "minLength": 4,
                "maxLength": 10,
                "label": "User Code (1)",
            },
            "value": "**********",
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
