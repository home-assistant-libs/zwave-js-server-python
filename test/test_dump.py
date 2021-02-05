"""Test the dump helper."""
from unittest.mock import call

from zwave_js_server.dump import dump_msgs


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
