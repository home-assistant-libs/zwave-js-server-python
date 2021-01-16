"""Test lock utility functions."""
from unittest.mock import patch

import pytest

from zwave_js_server.const import ATTR_CODE_SLOT, ATTR_IN_USE, ATTR_NAME, ATTR_USERCODE
from zwave_js_server.exceptions import NotFoundError
from zwave_js_server.util.lock import (
    get_code_slots,
    get_usercode,
    get_usercodes,
    set_usercode,
)

CODE_SLOT_NAME = "User Code ({})"


def test_get_code_slots(lock_schlage_be469):
    """Test get_code_slots utility function."""
    node = lock_schlage_be469
    code_slots = get_code_slots(node)
    for x in range(0, 30):
        code_slot = x + 1
        in_use = False
        if x < 3:
            in_use = True
        assert code_slots[x] == {
            ATTR_CODE_SLOT: code_slot,
            ATTR_IN_USE: in_use,
            ATTR_NAME: CODE_SLOT_NAME.format(code_slot),
        }


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
    code_slots = get_usercodes(node)
    for x in range(0, 30):
        code_slot = x + 1
        in_use = False
        usercode = None
        if x < 3:
            in_use = True
            usercode = "**********"
        assert code_slots[x] == {
            ATTR_CODE_SLOT: code_slot,
            ATTR_IN_USE: in_use,
            ATTR_NAME: CODE_SLOT_NAME.format(code_slot),
            ATTR_USERCODE: usercode,
        }


async def test_set_usercode(lock_schlage_be469):
    """Test set_usercode utility function."""
    node = lock_schlage_be469
    with patch("zwave_js_server.client.Client.async_send_command") as cmd:
        # Test valid code
        await set_usercode(node, 1, "1234")
        assert len(cmd.call_args_list) == 1
        args = cmd.call_args[0][0]
        assert args["command"] == "node.set_value"
        assert args["nodeId"] == 20
        assert args["valueId"] == {
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
        }
        assert args["value"] == "1234"

        cmd.reset_mock()

        # Test invalid code slot
        with pytest.raises(NotFoundError):
            await set_usercode(node, 100, "1234")
        assert len(cmd.call_args_list) == 0

        # Test invalid code length
        with pytest.raises(ValueError):
            await set_usercode(node, 1, "123")
        assert len(cmd.call_args_list) == 0
