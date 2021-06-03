"""Test the dump helper."""
import asyncio
from unittest.mock import AsyncMock, call

from aiohttp.client import ClientSession
import pytest

from zwave_js_server.dump import dump_msgs

# pylint: disable=too-many-arguments


@pytest.fixture(name="event")
def event_fixture():
    """Return a received event from the websocket client."""
    return {
        "type": "event",
        "event": {
            "source": "node",
            "event": "value updated",
            "nodeId": 52,
            "args": {
                "commandClassName": "Basic",
                "commandClass": 32,
                "endpoint": 0,
                "property": "currentValue",
                "newValue": 255,
                "prevValue": 255,
                "propertyName": "currentValue",
            },
        },
    }


@pytest.fixture(name="no_get_log_config_client_session")
def no_get_log_config_client_session_fixture(no_get_log_config_ws_client):
    """Mock an aiohttp client session without calling get_log_config."""
    no_get_log_config_client_session = AsyncMock(spec_set=ClientSession)
    no_get_log_config_client_session.ws_connect.side_effect = AsyncMock(
        return_value=no_get_log_config_ws_client
    )
    return no_get_log_config_client_session


async def test_dump(
    no_get_log_config_client_session,
    result,
    url,
    version_data,
    set_api_schema_data,
    no_get_log_config_ws_client,
):
    """Test the dump function."""
    messages = await dump_msgs(url, no_get_log_config_client_session)

    assert no_get_log_config_ws_client.receive_json.call_count == 3
    assert no_get_log_config_ws_client.send_json.call_count == 2
    assert no_get_log_config_ws_client.send_json.call_args == call(
        {"command": "start_listening", "messageId": "listen-id"}
    )
    assert no_get_log_config_ws_client.close.call_count == 1
    assert messages
    assert len(messages) == 3
    assert messages[0] == version_data
    assert messages[1] == set_api_schema_data
    assert messages[2] == result


async def test_dump_timeout(
    no_get_log_config_client_session,
    result,
    url,
    event,
    version_data,
    set_api_schema_data,
    no_get_log_config_ws_client,
):
    """Test the dump function with timeout."""
    to_receive = asyncio.Queue()
    for message in (version_data, set_api_schema_data, result, event):
        to_receive.put_nowait(message)

    async def receive_json():
        return await to_receive.get()

    no_get_log_config_ws_client.receive_json = AsyncMock(side_effect=receive_json)
    messages = await dump_msgs(url, no_get_log_config_client_session, 0.05)

    assert no_get_log_config_ws_client.receive_json.call_count == 5
    assert no_get_log_config_ws_client.send_json.call_count == 2
    assert no_get_log_config_ws_client.send_json.call_args == call(
        {"command": "start_listening", "messageId": "listen-id"}
    )
    assert no_get_log_config_ws_client.close.call_count == 1
    assert messages
    assert len(messages) == 4
    assert messages[0] == version_data
    assert messages[1] == set_api_schema_data
    assert messages[2] == result
    assert messages[3] == event
