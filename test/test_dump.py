"""Test the dump helper."""
import asyncio
from unittest.mock import AsyncMock, call

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


async def test_dump(client_session, result, url, version_data, ws_client):
    """Test the dump function."""
    messages = await dump_msgs(url, client_session)

    assert ws_client.receive_json.call_count == 2
    assert ws_client.send_json.call_count == 1
    assert ws_client.send_json.call_args == call({"command": "start_listening"})
    assert ws_client.close.call_count == 1
    assert messages
    assert len(messages) == 2
    assert messages[0] == version_data
    assert messages[1] == result


async def test_dump_timeout(
    client_session, result, url, event, version_data, ws_client
):
    """Test the dump function with timeout."""
    to_receive = asyncio.Queue()
    for message in (version_data, result, event):
        to_receive.put_nowait(message)

    async def receive_json():
        return await to_receive.get()

    ws_client.receive_json = AsyncMock(side_effect=receive_json)
    messages = await dump_msgs(url, client_session, 0.05)

    assert ws_client.receive_json.call_count == 4
    assert ws_client.send_json.call_count == 1
    assert ws_client.send_json.call_args == call({"command": "start_listening"})
    assert ws_client.close.call_count == 1
    assert messages
    assert len(messages) == 3
    assert messages[0] == version_data
    assert messages[1] == result
    assert messages[2] == event
