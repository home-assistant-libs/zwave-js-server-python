"""Test access-control models and API wrappers."""

from __future__ import annotations

from typing import Any

from zwave_js_server.const import SupervisionStatus
from zwave_js_server.const.command_class.access_control import (
    AssignCredentialResult,
    SetCredentialResult,
    SetUserResult,
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
    UserCredentialCapability,
    UserData,
    UserDeletedArgs,
    deserialize_credential_data,
    serialize_credential_data,
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
            "supportsCredentialAssignment": True,
        }
    )

    assert capabilities.supports_admin_code
    assert not capabilities.supports_admin_code_deactivation
    assert capabilities.supports_credential_assignment
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
                "supportsCredentialAssignment": True,
            }
        },
    )

    assert await endpoint.access_control.is_supported()
    user_capabilities = await node.access_control.get_user_capabilities_cached()
    credential_capabilities = (
        await node.access_control.get_credential_capabilities_cached()
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
    assert credential_capabilities.supports_credential_assignment
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

    user = await node.access_control.get_user(3)
    credential = await node.access_control.get_credential(
        UserCredentialType.PIN_CODE, 0
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


async def test_access_control_set_user(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test set_user returns SetUserResult."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.set_user",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": SetUserResult.OK},
    )

    result = await node.access_control.set_user(
        3,
        SetUserOptions(
            active=True,
            user_type=UserCredentialUserType.GENERAL,
            user_name="Guest",
            credential_rule=UserCredentialRule.SINGLE,
        ),
    )

    assert result is SetUserResult.OK
    assert ack_commands == [
        {
            "command": "endpoint.access_control.set_user",
            "nodeId": node.node_id,
            "endpoint": 0,
            "userId": 3,
            "options": {
                "active": True,
                "userType": UserCredentialUserType.GENERAL,
                "userName": "Guest",
                "credentialRule": UserCredentialRule.SINGLE,
            },
            "messageId": uuid4,
        }
    ]


async def test_access_control_delete_user(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test delete_user returns SetUserResult."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.delete_user",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": SetUserResult.OK},
    )

    result = await node.access_control.delete_user(3)

    assert result is SetUserResult.OK
    assert ack_commands == [
        {
            "command": "endpoint.access_control.delete_user",
            "nodeId": node.node_id,
            "endpoint": 0,
            "userId": 3,
            "messageId": uuid4,
        }
    ]


async def test_access_control_delete_all_users(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test delete_all_users returns SetUserResult."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.delete_all_users",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": SetUserResult.OK},
    )

    result = await node.access_control.delete_all_users()

    assert result is SetUserResult.OK
    assert ack_commands == [
        {
            "command": "endpoint.access_control.delete_all_users",
            "nodeId": node.node_id,
            "endpoint": 0,
            "messageId": uuid4,
        }
    ]


async def test_access_control_set_credential(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test set_credential returns SetCredentialResult and wraps bytes payload."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.set_credential",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": SetCredentialResult.OK},
    )

    result = await node.access_control.set_credential(
        3, UserCredentialType.PIN_CODE, 0, b"1234"
    )

    assert result is SetCredentialResult.OK
    assert ack_commands == [
        {
            "command": "endpoint.access_control.set_credential",
            "nodeId": node.node_id,
            "endpoint": 0,
            "userId": 3,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 0,
            "data": {"type": "Buffer", "data": [49, 50, 51, 52]},
            "messageId": uuid4,
        }
    ]


async def test_access_control_delete_credential(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test delete_credential returns SetCredentialResult."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.delete_credential",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": SetCredentialResult.OK},
    )

    result = await node.access_control.delete_credential(
        3, UserCredentialType.PIN_CODE, 0
    )

    assert result is SetCredentialResult.OK
    assert ack_commands == [
        {
            "command": "endpoint.access_control.delete_credential",
            "nodeId": node.node_id,
            "endpoint": 0,
            "userId": 3,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 0,
            "messageId": uuid4,
        }
    ]


async def test_access_control_assign_credential(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test assign_credential returns AssignCredentialResult."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.assign_credential",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": AssignCredentialResult.OK},
    )

    result = await node.access_control.assign_credential(
        UserCredentialType.PIN_CODE, 1, 5
    )

    assert result is AssignCredentialResult.OK
    assert ack_commands == [
        {
            "command": "endpoint.access_control.assign_credential",
            "nodeId": node.node_id,
            "endpoint": 0,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 1,
            "destinationUserId": 5,
            "messageId": uuid4,
        }
    ]


async def test_access_control_start_credential_learn(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test start_credential_learn returns supervision result."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.start_credential_learn",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": {"status": SupervisionStatus.SUCCESS}},
    )

    result = await node.access_control.start_credential_learn(
        3, UserCredentialType.PIN_CODE, 0, 30
    )

    assert result is not None
    assert result.status is SupervisionStatus.SUCCESS
    assert ack_commands == [
        {
            "command": "endpoint.access_control.start_credential_learn",
            "nodeId": node.node_id,
            "endpoint": 0,
            "userId": 3,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 0,
            "timeout": 30,
            "messageId": uuid4,
        }
    ]


async def test_access_control_cancel_credential_learn(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test cancel_credential_learn returns supervision result."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.cancel_credential_learn",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": {"status": SupervisionStatus.SUCCESS}},
    )

    result = await node.access_control.cancel_credential_learn()

    assert result is not None
    assert result.status is SupervisionStatus.SUCCESS
    assert ack_commands == [
        {
            "command": "endpoint.access_control.cancel_credential_learn",
            "nodeId": node.node_id,
            "endpoint": 0,
            "messageId": uuid4,
        }
    ]


async def test_access_control_set_admin_code(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test set_admin_code returns supervision result."""
    node = lock_schlage_be469
    ack_commands = mock_command(
        {
            "command": "endpoint.access_control.set_admin_code",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"result": {"status": SupervisionStatus.SUCCESS}},
    )

    result = await node.access_control.set_admin_code("2468")

    assert result is not None
    assert result.status is SupervisionStatus.SUCCESS
    assert ack_commands == [
        {
            "command": "endpoint.access_control.set_admin_code",
            "nodeId": node.node_id,
            "endpoint": 0,
            "code": "2468",
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

    assert await node.access_control.get_admin_code() == "2468"
    assert ack_commands == [
        {
            "command": "endpoint.access_control.get_admin_code",
            "nodeId": node.node_id,
            "endpoint": 0,
            "messageId": uuid4,
        }
    ]


def _dispatch_access_control_event(
    node: Node, event_type: str, args: dict[str, Any]
) -> dict[str, Any]:
    """Dispatch a schema-48 access-control event and return the observed payload."""
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
    return event_data


def test_access_control_user_added_event(lock_schlage_be469: Node) -> None:
    """Test `user added` event normalization."""
    event_data = _dispatch_access_control_event(
        lock_schlage_be469,
        "user added",
        {
            "userId": 3,
            "active": True,
            "userType": UserCredentialUserType.GENERAL,
            "userName": "Guest",
            "credentialRule": UserCredentialRule.SINGLE,
        },
    )
    parsed = event_data["args"]
    assert isinstance(parsed, UserData)
    assert parsed.user_id == 3
    assert parsed.user_type is UserCredentialUserType.GENERAL
    assert parsed.user_name == "Guest"
    assert parsed.credential_rule is UserCredentialRule.SINGLE


def test_access_control_user_modified_event(lock_schlage_be469: Node) -> None:
    """Test `user modified` event normalization."""
    event_data = _dispatch_access_control_event(
        lock_schlage_be469,
        "user modified",
        {
            "userId": 3,
            "active": False,
            "userType": UserCredentialUserType.EXPIRING,
            "userName": "Temp",
            "credentialRule": UserCredentialRule.DUAL,
            "expiringTimeoutMinutes": 30,
        },
    )
    parsed = event_data["args"]
    assert isinstance(parsed, UserData)
    assert parsed.user_id == 3
    assert parsed.user_type is UserCredentialUserType.EXPIRING
    assert parsed.expiring_timeout_minutes == 30


def test_access_control_user_deleted_event(lock_schlage_be469: Node) -> None:
    """Test `user deleted` event normalization."""
    event_data = _dispatch_access_control_event(
        lock_schlage_be469, "user deleted", {"userId": 3}
    )
    parsed = event_data["args"]
    assert isinstance(parsed, UserDeletedArgs)
    assert parsed.user_id == 3


def test_access_control_credential_added_event(lock_schlage_be469: Node) -> None:
    """Test `credential added` event normalization with bytes payload."""
    event_data = _dispatch_access_control_event(
        lock_schlage_be469,
        "credential added",
        {
            "userId": 3,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 0,
            "data": {"type": "Buffer", "data": [49, 50, 51, 52]},
        },
    )
    parsed = event_data["args"]
    assert isinstance(parsed, CredentialChangedArgs)
    assert parsed.user_id == 3
    assert parsed.credential_type is UserCredentialType.PIN_CODE
    assert parsed.data == b"1234"


def test_access_control_credential_modified_event(lock_schlage_be469: Node) -> None:
    """Test `credential modified` event normalization with str payload."""
    event_data = _dispatch_access_control_event(
        lock_schlage_be469,
        "credential modified",
        {
            "userId": 3,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 0,
            "data": "2468",
        },
    )
    parsed = event_data["args"]
    assert isinstance(parsed, CredentialChangedArgs)
    assert parsed.user_id == 3
    assert parsed.credential_type is UserCredentialType.PIN_CODE
    assert parsed.data == "2468"


def test_access_control_credential_deleted_event(lock_schlage_be469: Node) -> None:
    """Test `credential deleted` event normalization."""
    event_data = _dispatch_access_control_event(
        lock_schlage_be469,
        "credential deleted",
        {
            "userId": 3,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 0,
        },
    )
    parsed = event_data["args"]
    assert isinstance(parsed, CredentialDeletedArgs)
    assert parsed.credential_slot == 0
    assert parsed.credential_type is UserCredentialType.PIN_CODE


def test_access_control_credential_learn_progress_event(
    lock_schlage_be469: Node,
) -> None:
    """Test `credential learn progress` event normalization."""
    event_data = _dispatch_access_control_event(
        lock_schlage_be469,
        "credential learn progress",
        {
            "userId": 3,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 0,
            "stepsRemaining": 2,
            "status": UserCredentialLearnStatus.STEP_RETRY,
        },
    )
    parsed = event_data["args"]
    assert isinstance(parsed, CredentialLearnProgressArgs)
    assert parsed.steps_remaining == 2
    assert parsed.status is UserCredentialLearnStatus.STEP_RETRY


def test_access_control_credential_learn_completed_event(
    lock_schlage_be469: Node,
) -> None:
    """Test `credential learn completed` event normalization."""
    event_data = _dispatch_access_control_event(
        lock_schlage_be469,
        "credential learn completed",
        {
            "userId": 3,
            "credentialType": UserCredentialType.PIN_CODE,
            "credentialSlot": 0,
            "status": UserCredentialLearnStatus.SUCCESS,
            "success": True,
        },
    )
    parsed = event_data["args"]
    assert isinstance(parsed, CredentialLearnCompletedArgs)
    assert parsed.success
    assert parsed.status is UserCredentialLearnStatus.SUCCESS


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
    mock_command(
        {
            "command": "endpoint.access_control.get_credentials_by_type",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"credentials": [credential_payload]},
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_credentials_by_type_cached",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"credentials": [credential_payload]},
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_all_credentials",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"credentials": [credential_payload]},
    )
    mock_command(
        {
            "command": "endpoint.access_control.get_all_credentials_cached",
            "nodeId": node.node_id,
            "endpoint": 0,
        },
        {"credentials": [credential_payload]},
    )

    assert await node.access_control.get_users() == [UserData.from_dict(user_payload)]
    assert await node.access_control.get_users_cached() == [
        UserData.from_dict(user_payload)
    ]
    assert await node.access_control.get_user_cached(1) == UserData.from_dict(
        user_payload
    )
    assert await node.access_control.get_credentials(1) == [
        CredentialData.from_dict(credential_payload)
    ]
    assert await node.access_control.get_credentials_cached(1) == [
        CredentialData.from_dict(credential_payload)
    ]
    assert await node.access_control.get_credential_cached(
        UserCredentialType.PIN_CODE, 0
    ) == CredentialData.from_dict(credential_payload)
    assert await node.access_control.get_credentials_by_type(
        UserCredentialType.PIN_CODE
    ) == [CredentialData.from_dict(credential_payload)]
    assert await node.access_control.get_credentials_by_type_cached(
        UserCredentialType.PIN_CODE
    ) == [CredentialData.from_dict(credential_payload)]
    assert await node.access_control.get_all_credentials() == [
        CredentialData.from_dict(credential_payload)
    ]
    assert await node.access_control.get_all_credentials_cached() == [
        CredentialData.from_dict(credential_payload)
    ]


async def test_access_control_none_results(
    lock_schlage_be469: Node, mock_command: MockCommandProtocol
) -> None:
    """Test that missing user/credential/admin-code responses return None."""
    node = lock_schlage_be469
    for command in (
        "get_user",
        "get_user_cached",
        "get_credential",
        "get_credential_cached",
    ):
        mock_command(
            {
                "command": f"endpoint.access_control.{command}",
                "nodeId": node.node_id,
                "endpoint": 0,
            },
            {},
        )

    assert await node.access_control.get_user(1) is None
    assert await node.access_control.get_user_cached(1) is None
    assert (
        await node.access_control.get_credential(UserCredentialType.PIN_CODE, 0) is None
    )
    assert (
        await node.access_control.get_credential_cached(UserCredentialType.PIN_CODE, 0)
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
        {"result": SetCredentialResult.OK},
    )

    result = await node.access_control.set_credential(
        3, UserCredentialType.PIN_CODE, 0, "1234"
    )

    assert result is SetCredentialResult.OK
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

    result = await node.access_control.start_credential_learn(
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


def test_credential_data_serialize_helpers() -> None:
    """Test (de)serialization helpers for credential payloads."""

    assert deserialize_credential_data(None) is None
    assert deserialize_credential_data("abcd") == "abcd"
    assert deserialize_credential_data({"type": "Buffer", "data": [1, 2]}) == bytes(
        [1, 2]
    )
    assert serialize_credential_data("abcd") == "abcd"
    assert serialize_credential_data(b"\x01\x02") == {
        "type": "Buffer",
        "data": [1, 2],
    }


def test_user_credential_capability_round_trip() -> None:
    """Test UserCredentialCapability round-trips via from_dict/to_dict."""

    full_payload = {
        "numberOfCredentialSlots": 5,
        "minCredentialLength": 4,
        "maxCredentialLength": 8,
        "maxCredentialHashLength": 0,
        "supportsCredentialLearn": True,
        "credentialLearnRecommendedTimeout": 30,
        "credentialLearnNumberOfSteps": 3,
    }
    minimal_payload = {
        "numberOfCredentialSlots": 5,
        "minCredentialLength": 4,
        "maxCredentialLength": 8,
        "maxCredentialHashLength": 0,
        "supportsCredentialLearn": False,
    }

    assert UserCredentialCapability.from_dict(full_payload).to_dict() == full_payload
    assert (
        UserCredentialCapability.from_dict(minimal_payload).to_dict() == minimal_payload
    )


def test_credential_capabilities_to_dict() -> None:
    """Test CredentialCapabilities serialization including nested capability."""

    payload = {
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
        "supportsCredentialAssignment": True,
    }

    assert CredentialCapabilities.from_dict(payload).to_dict() == payload


def test_user_capabilities_to_dict() -> None:
    """Test UserCapabilities serialization with and without optional fields."""

    full_payload = {
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
    minimal_payload = {
        "maxUsers": 25,
        "supportedUserTypes": [],
        "supportedCredentialRules": [],
    }

    assert UserCapabilities.from_dict(full_payload).to_dict() == full_payload
    assert UserCapabilities.from_dict(minimal_payload).to_dict() == minimal_payload


def test_user_data_to_dict() -> None:
    """Test UserData serialization with all and minimal fields."""

    full_payload = {
        "userId": 3,
        "active": True,
        "userType": UserCredentialUserType.EXPIRING,
        "userName": "Temp",
        "credentialRule": UserCredentialRule.DUAL,
        "expiringTimeoutMinutes": 30,
    }
    minimal_payload = {
        "userId": 7,
        "active": False,
        "userType": UserCredentialUserType.GENERAL,
    }

    assert UserData.from_dict(full_payload).to_dict() == full_payload
    assert UserData.from_dict(minimal_payload).to_dict() == minimal_payload


def test_set_user_options_to_dict_with_expiring_timeout() -> None:
    """Test SetUserOptions serialization includes expiringTimeoutMinutes."""

    options = SetUserOptions(
        active=True,
        user_type=UserCredentialUserType.EXPIRING,
        user_name="Temp",
        credential_rule=UserCredentialRule.DUAL,
        expiring_timeout_minutes=15,
    )

    assert options.to_dict() == {
        "active": True,
        "userType": UserCredentialUserType.EXPIRING,
        "userName": "Temp",
        "credentialRule": UserCredentialRule.DUAL,
        "expiringTimeoutMinutes": 15,
    }


def test_set_user_options_to_dict_empty() -> None:
    """Test SetUserOptions serialization omits all unset fields."""

    assert SetUserOptions().to_dict() == {}


def test_set_user_options_to_dict_partial() -> None:
    """Test SetUserOptions serialization omits fields left as None."""

    options = SetUserOptions(
        active=False,
        user_name="Guest",
    )

    assert options.to_dict() == {
        "active": False,
        "userName": "Guest",
    }


def test_credential_data_to_dict() -> None:
    """Test CredentialData serialization for bytes, str, and missing data."""

    bytes_payload = {
        "userId": 3,
        "type": UserCredentialType.PIN_CODE,
        "slot": 0,
        "data": {"type": "Buffer", "data": [49, 50, 51, 52]},
    }
    str_payload = {
        "userId": 3,
        "type": UserCredentialType.PIN_CODE,
        "slot": 0,
        "data": "1234",
    }
    no_data_payload = {
        "userId": 3,
        "type": UserCredentialType.PIN_CODE,
        "slot": 0,
    }

    assert CredentialData.from_dict(bytes_payload).to_dict() == bytes_payload
    assert CredentialData.from_dict(str_payload).to_dict() == str_payload
    assert CredentialData.from_dict(no_data_payload).to_dict() == no_data_payload


def test_user_deleted_args_to_dict() -> None:
    """Test UserDeletedArgs round-trips via from_dict/to_dict."""

    payload = {"userId": 3}
    assert UserDeletedArgs.from_dict(payload).to_dict() == payload


def test_credential_changed_args_to_dict() -> None:
    """Test CredentialChangedArgs serialization for bytes, str, and missing data."""

    bytes_payload = {
        "userId": 3,
        "credentialType": UserCredentialType.PIN_CODE,
        "credentialSlot": 0,
        "data": {"type": "Buffer", "data": [49, 50, 51, 52]},
    }
    str_payload = {
        "userId": 3,
        "credentialType": UserCredentialType.PIN_CODE,
        "credentialSlot": 0,
        "data": "2468",
    }
    no_data_payload = {
        "userId": 3,
        "credentialType": UserCredentialType.PIN_CODE,
        "credentialSlot": 0,
    }

    assert CredentialChangedArgs.from_dict(bytes_payload).to_dict() == bytes_payload
    assert CredentialChangedArgs.from_dict(str_payload).to_dict() == str_payload
    assert CredentialChangedArgs.from_dict(no_data_payload).to_dict() == no_data_payload


def test_credential_deleted_args_to_dict() -> None:
    """Test CredentialDeletedArgs round-trips via from_dict/to_dict."""

    payload = {
        "userId": 3,
        "credentialType": UserCredentialType.PIN_CODE,
        "credentialSlot": 0,
    }
    assert CredentialDeletedArgs.from_dict(payload).to_dict() == payload


def test_credential_learn_progress_args_to_dict() -> None:
    """Test CredentialLearnProgressArgs round-trips via from_dict/to_dict."""

    payload = {
        "userId": 3,
        "credentialType": UserCredentialType.PIN_CODE,
        "credentialSlot": 0,
        "stepsRemaining": 2,
        "status": UserCredentialLearnStatus.STEP_RETRY,
    }
    assert CredentialLearnProgressArgs.from_dict(payload).to_dict() == payload


def test_credential_learn_completed_args_to_dict() -> None:
    """Test CredentialLearnCompletedArgs round-trips via from_dict/to_dict."""

    payload = {
        "userId": 3,
        "credentialType": UserCredentialType.PIN_CODE,
        "credentialSlot": 0,
        "status": UserCredentialLearnStatus.SUCCESS,
        "success": True,
    }
    assert CredentialLearnCompletedArgs.from_dict(payload).to_dict() == payload
