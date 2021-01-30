"""Test the client."""
from zwave_js_server.client import Client


async def test_connect(client_session, ws_client, url, version_data):
    """Test client connect."""
    ws_client.receive_json.return_value = version_data
    client = Client(url, client_session)

    await client.connect()

    assert client.connected
