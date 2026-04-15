"""Test access-control models and API wrappers."""

from __future__ import annotations

from typing import Any

import pytest

from zwave_js_server.const import SupervisionStatus
from zwave_js_server.const.command_class.access_control import (
    UserCredentialLearnStatus,
    UserCredentialRule,
    UserCredentialType,
    UserCredentialUserType,
)
from zwave_js_server.event import Event
from zwave_js_server.model.access_control import (
    CredentialCapabilities,
    CredentialChangedArgs,
    CredentialData,
    CredentialDeletedArgs,
    CredentialLearnCompletedArgs,
    CredentialLearnProgressArgs,
    SetUserOptions,
    UserCapabilities,
    UserData,
    UserDeletedArgs,
)
from zwave_js_server.model.node import Node

from ..common import MockCommandProtocol


def test_credential_capabilities_from_dict() -> None:
    """Test credential capability map normalization."""

    capabilities = CredentialCapabilities.from_dict(
        {
            "supportedCredentialTypes": {
                str(UserCredentialType.PIN_CODE.value): {
                    "numberOfCredentialSlots": 2,
                    "minCredentialLength": 4,
                    "maxCredentialLength": 8,
                    "maxCredentialHashLength": 0,
                    "supportsCredentialLearn": True,
                    "credentialLearnRecommendedTimeout": 30,
                    "credentialLearnNumberOfSteps": 3,
                }
            },
            "supportsAdminCode": True,
            "supportsAdminCodeDeactivation": False,
        }
    )

    assert capabilities.supports_admin_code
    assert not capabilities.supports_admin_code_deactivation
    assert UserCredentialType.PIN_CODE in capabilities.supported_credential_types
    pin_code = capabilities.supported_credential_types[UserCredentialType.PIN_CODE]
    assert pin_code.number_of_credential_slots == 2
    assert pin_code.supports_credential_learn
    assert pin_code.credential_learn_number_of_steps == 3


async def test_access_control_support_and_capabilities(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test support checks and cached capability commands."""

    node = lock_schlage_be469
    endpoint = node.endpoints[0]
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.is_supported",
            "nodeId": node.node_id,
            "endpoint": endpoint.index,
        },
        {"supported": True},
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_user_capabilities_cached",
            "nodeId": node.node_id,
            "endpoint": endpoint.index,
        },
        {
            "capabilities": {
                "maxUsers": 25,
                "supportedUserTypes": [
                    UserCredentialUserType.GENERAL,
                    UserCredentialUserType.EXPIRING,
                ],
                "maxUserNameLength": 10,
                "supportedCredentialRules": [
                    UserCredentialRule.SINGLE,
                    UserCredentialRule.DUAL,
                ],
            }
        },
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_credential_capabilities_cached",
            "nodeId": node.node_id,
            "endpoint": endpoint.index,
        },
        {
            "capabilities": {
                "supportedCredentialTypes": {
                    str(UserCredentialType.PIN_CODE.value): {
                        "numberOfCredentialSlots": 5,
                        "minCredentialLength": 4,
                        "maxCredentialLength": 8,
                        "maxCredentialHashLength": 0,
                        "supportsCredentialLearn": False,
                    }
                },
                "supportsAdminCode": True,
                "supportsAdminCodeDeactivation": True,
            }
        },
    )

    assert await endpoint.access_control.async_is_supported()
    user_capabilities = await node.access_control.async_get_user_capabilities_cached()
    credential_capabilities = (
        await node.access_control.async_get_credential_capabilities_cached()
    )

    assert len(ack_commands) == 3
    assert ack_commands[0] == {
        "command": "endpoint.access_control.is_supported",
        "nodeId": node.node_id,
        "endpoint": endpoint.index,
        "messageId": uuid4,
    }
    assert ack_commands[1]["command"] == (
        "endpoint.access_control.get_user_capabilities_cached"
    )
    assert ack_commands[2]["command"] == (
        "endpoint.access_control.get_credential_capabilities_cached"
    )

    assert user_capabilities == UserCapabilities(
        max_users=25,
        supported_user_types=[
            UserCredentialUserType.GENERAL,
            UserCredentialUserType.EXPIRING,
        ],
        max_user_name_length=10,
        supported_credential_rules=[
            UserCredentialRule.SINGLE,
            UserCredentialRule.DUAL,
        ],
    )
    assert credential_capabilities.supports_admin_code
    assert credential_capabilities.supports_admin_code_deactivation
    assert (
        credential_capabilities.supported_credential_types[
            UserCredentialType.PIN_CODE
        ].number_of_credential_slots
        == 5
    )


async def test_access_control_get_user_and_credential(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test fetching access-control users and credentials through node proxies."""

    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.get_user",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {
            "user": {
                "userId": 3,
                "active": True,
                "userType": UserCredentialUserType.EXPIRING,
                "userName": "Guest",
                "credentialRule": UserCredentialRule.DUAL,
                "expiringTimeoutMinutes": 60,
            }
        },
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_credential",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {
            "credential": {
                "userId": 3,
                "type": UserCredentialType.PIN_CODE,
                "slot": 0,
                "data": {"type": "Buffer", "data": [49, 50, 51, 52]},
            }
        },
    )

    user = await node.access_control.async_get_user(3)
    credential = await node.access_control.async_get_credential(
        3, UserCredentialType.PIN_CODE, 0
    )

    assert len(ack_commands) == 2
    assert ack_commands[0] == {
        "command": "endpoint.access_control.get_user",
        "nodeId": node.node_id,
        "endpoint": 0,
        "userId": 3,
        "messageId": uuid4,
    }
    assert ack_commands[1] == {
        "command": "endpoint.access_control.get_credential",
        "nodeId": node.node_id,
        "endpoint": 0,
        "userId": 3,
        "credentialType": UserCredentialType.PIN_CODE,
        "credentialSlot": 0,
        "messageId": uuid4,
    }
    assert user == UserData(
        user_id=3,
        active=True,
        user_type=UserCredentialUserType.EXPIRING,
        user_name="Guest",
        credential_rule=UserCredentialRule.DUAL,
        expiring_timeout_minutes=60,
    )
    assert credential == CredentialData(
        user_id=3,
        type=UserCredentialType.PIN_CODE,
        slot=0,
        data=b"1234",
    )


@pytest.mark.parametrize(
    ("command", "expected_payload", "call"),
    [
        (
            "set_user",
            {
                "userId": 3,
                "options": {
                    "active": True,
                    "userType": UserCredentialUserType.GENERAL,
                    "userName": "Guest",
                    "credentialRule": UserCredentialRule.SINGLE,
                },
            },
            "set_user",
        ),
        (
            "delete_user",
            {"userId": 3},
            "delete_user",
        ),
        (
            "delete_all_users",
            {},
            "delete_all_users",
        ),
        (
            "set_credential",
            {
                "userId": 3,
                "credentialType": UserCredentialType.PIN_CODE,
                "credentialSlot": 0,
                "data": {"type": "Buffer", "data": [49, 50, 51, 52]},
            },
            "set_credential",
        ),
        (
            "delete_credential",
            {
                "userId": 3,
                "credentialType": UserCredentialType.PIN_CODE,
                "credentialSlot": 0,
            },
            "delete_credential",
        ),
        (
            "start_credential_learn",
            {
                "userId": 3,
                "credentialType": UserCredentialType.PIN_CODE,
                "credentialSlot": 0,
                "timeout": 30,
            },
            "start_credential_learn",
        ),
        (
            "cancel_credential_learn",
            {},
            "cancel_credential_learn",
        ),
        (
            "set_admin_code",
            {"code": "2468"},
            "set_admin_code",
        ),
    ],
)
async def test_access_control_mutation_commands(
    lock_schlage_be469: Node,
    mock_command: MockCommandProtocol,
    uuid4: str,
    command: str,
    expected_payload: dict[str, Any],
    call: str,
) -> None:
    """Test access-control mutation commands and supervision parsing."""

    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": f"endpoint.access_control.{command}",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": {"status": SupervisionStatus.SUCCESS}},
    )

    if call == "set_user":
        result = await node.access_control.async_set_user(
            3,
            SetUserOptions(
                active=True,
                user_type=UserCredentialUserType.GENERAL,
                user_name="Guest",
                credential_rule=UserCredentialRule.SINGLE,
            ),
        )
    elif call == "delete_user":
        result = await node.access_control.async_delete_user(3)
    elif call == "delete_all_users":
        result = await node.access_control.async_delete_all_users()
    elif call == "set_credential":
        result = await node.access_control.async_set_credential(
            3, UserCredentialType.PIN_CODE, 0, b"1234"
        )
    elif call == "delete_credential":
        result = await node.access_control.async_delete_credential(
            3, UserCredentialType.PIN_CODE, 0
        )
    elif call == "start_credential_learn":
        result = await node.access_control.async_start_credential_learn(
            3, UserCredentialType.PIN_CODE, 0, 30
        )
    elif call == "cancel_credential_learn":
        result = await node.access_control.async_cancel_credential_learn()
    else:
        result = await node.access_control.async_set_admin_code("2468")

    assert result is not None
    assert result.status is SupervisionStatus.SUCCESS
    assert ack_commands == [
        {
            "command": f"endpoint.access_control.{command}",
            "nodeId": node.node_id,
            "endpoint": 0,
            **expected_payload,
            "messageId": uuid4,
        }
    ]


async def test_access_control_get_admin_code(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test fetching access-control admin code."""

    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.get_admin_code",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"code": "2468"},
    )

    assert await node.access_control.async_get_admin_code() == "2468"
    assert ack_commands == [
        {
            "command": "endpoint.access_control.get_admin_code",
            "nodeId": node.node_id,
            "endpoint": 0,
            "messageId": uuid4,
        }
    ]


@pytest.mark.parametrize(
    ("event_type", "args", "expected_type"),
    [
        (
            "user added",
            {
                "userId": 3,
                "active": True,
                "userType": UserCredentialUserType.GENERAL,
                "userName": "Guest",
                "credentialRule": UserCredentialRule.SINGLE,
            },
            UserData,
        ),
        (
            "user modified",
            {
                "userId": 3,
                "active": False,
                "userType": UserCredentialUserType.EXPIRING,
                "userName": "Temp",
                "credentialRule": UserCredentialRule.DUAL,
                "expiringTimeoutMinutes": 30,
            },
            UserData,
        ),
        ("user deleted", {"userId": 3}, UserDeletedArgs),
        (
            "credential added",
            {
                "userId": 3,
                "credentialType": UserCredentialType.PIN_CODE,
                "credentialSlot": 0,
                "data": {"type": "Buffer", "data": [49, 50, 51, 52]},
            },
            CredentialChangedArgs,
        ),
        (
            "credential modified",
            {
                "userId": 3,
                "credentialType": UserCredentialType.PIN_CODE,
                "credentialSlot": 0,
                "data": "2468",
            },
            CredentialChangedArgs,
        ),
        (
            "credential deleted",
            {
                "userId": 3,
                "credentialType": UserCredentialType.PIN_CODE,
                "credentialSlot": 0,
            },
            CredentialDeletedArgs,
        ),
        (
            "credential learn progress",
            {
                "userId": 3,
                "credentialType": UserCredentialType.PIN_CODE,
                "credentialSlot": 0,
                "stepsRemaining": 2,
                "status": UserCredentialLearnStatus.STEP_RETRY,
            },
            CredentialLearnProgressArgs,
        ),
        (
            "credential learn completed",
            {
                "userId": 3,
                "credentialType": UserCredentialType.PIN_CODE,
                "credentialSlot": 0,
                "status": UserCredentialLearnStatus.SUCCESS,
                "success": True,
            },
            CredentialLearnCompletedArgs,
        ),
    ],
)
def test_access_control_events(
    lock_schlage_be469: Node,
    event_type: str,
    args: dict[str, Any],
    expected_type: type[
        UserData
        | UserDeletedArgs
        | CredentialChangedArgs
        | CredentialDeletedArgs
        | CredentialLearnProgressArgs
        | CredentialLearnCompletedArgs
    ],
) -> None:
    """Test schema 48 access-control node event normalization."""

    node = lock_schlage_be469
    observed: list[dict[str, Any]] = []
    node.on(event_type, observed.append)

    node.receive_event(
        Event(
            event_type,
            {
                "source": "node",
                "event": event_type,
                "nodeId": node.node_id,
                "endpointIndex": 0,
                "args": args,
            },
        )
    )

    assert len(observed) == 1
    event_data = observed[0]
    assert event_data["node"] is node
    assert event_data["endpoint"] is node.endpoints[0]
    assert event_data["endpointIndex"] == 0
    parsed_args = event_data["args"]
    assert isinstance(parsed_args, expected_type)

    if isinstance(parsed_args, UserData):
        assert parsed_args.user_id == 3
        assert isinstance(parsed_args.user_type, UserCredentialUserType)
    elif isinstance(parsed_args, UserDeletedArgs):
        assert parsed_args.user_id == 3
    elif isinstance(parsed_args, CredentialChangedArgs):
        assert parsed_args.user_id == 3
        assert parsed_args.credential_type is UserCredentialType.PIN_CODE
        if event_type == "credential added":
            assert parsed_args.data == b"1234"
        else:
            assert parsed_args.data == "2468"
    elif isinstance(parsed_args, CredentialDeletedArgs):
        assert parsed_args.credential_slot == 0
        assert parsed_args.credential_type is UserCredentialType.PIN_CODE
    elif isinstance(parsed_args, CredentialLearnProgressArgs):
        assert parsed_args.steps_remaining == 2
        assert parsed_args.status is UserCredentialLearnStatus.STEP_RETRY
    else:
        assert parsed_args.success
        assert parsed_args.status is UserCredentialLearnStatus.SUCCESS


async def test_access_control_list_commands(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol
) -> None:
    """Test fetching lists of users and credentials (fresh and cached)."""
    node = lock_schlage_be469
    user_payload = {
        "userId": 1,
        "active": True,
        "userType": UserCredentialUserType.GENERAL,
        "userName": "Owner",
        "credentialRule": UserCredentialRule.SINGLE,
    }
    credential_payload = {
        "userId": 1,
        "type": UserCredentialType.PIN_CODE,
        "slot": 0,
        "data": "1234",
    }
    mock_command(
        {
            "command": "endpoint.access_control.get_users",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"users": [user_payload]},
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_users_cached",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"users": [user_payload]},
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_user_cached",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"user": user_payload},
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_credentials",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"credentials": [credential_payload]},
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_credentials_cached",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"credentials": [credential_payload]},
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_credential_cached",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"credential": credential_payload},
    )

    assert await node.access_control.async_get_users() == [
        UserData.from_dict(user_payload)
    ]
    assert await node.access_control.async_get_users_cached() == [
        UserData.from_dict(user_payload)
    ]
    assert await node.access_control.async_get_user_cached(1) == UserData.from_dict(
        user_payload
    )
    assert await node.access_control.async_get_credentials(1) == [
        CredentialData.from_dict(credential_payload)
    ]
    assert await node.access_control.async_get_credentials_cached(1) == [
        CredentialData.from_dict(credential_payload)
    ]
    assert await node.access_control.async_get_credential_cached(
        1, UserCredentialType.PIN_CODE, 0
    ) == CredentialData.from_dict(credential_payload)


async def test_access_control_none_results(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol
) -> None:
    """Test that missing user/credential/admin-code responses return None."""
    node = lock_schlage_be469
    mock_command(
        {
            "command": "endpoint.access_control.get_user",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {},
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_credential",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {},
    )

    assert await node.access_control.async_get_user(1) is None
    assert (
        await node.access_control.async_get_credential(
            1, UserCredentialType.PIN_CODE, 0
        )
        is None
    )


async def test_access_control_set_credential_str_data(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test that string credential payloads are sent without Buffer wrapping."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.set_credential",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": {"status": SupervisionStatus.SUCCESS}},
    )

    result = await node.access_control.async_set_credential(
        3, UserCredentialType.PIN_CODE, 0, "1234"
    )

    assert result is not None
    assert ack_commands == [
        {
            "command": "endpoint.access_control.set_credential",
            "nodeId": node.node_id,
            "endpoint": 0,
            "userId": 3,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 0,
            "data": "1234",
            "messageId": uuid4,
        }
    ]


async def test_access_control_start_credential_learn_no_timeout(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test that start_credential_learn omits timeout when not provided."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.start_credential_learn",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": {"status": SupervisionStatus.SUCCESS}},
    )

    result = await node.access_control.async_start_credential_learn(
        3, UserCredentialType.PIN_CODE, 0
    )

    assert result is not None
    assert "timeout" not in ack_commands[0]
    assert ack_commands == [
        {
            "command": "endpoint.access_control.start_credential_learn",
            "nodeId": node.node_id,
            "endpoint": 0,
            "userId": 3,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 0,
            "messageId": uuid4,
        }
    ]
