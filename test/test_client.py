"""Test the client."""
from aiohttp.client_exceptions import ClientError
import pytest

from zwave_js_server.client import Client
from zwave_js_server.exceptions import CannotConnect, InvalidServerVersion


async def test_connect(client_session, url):
    """Test client connect."""
    client = Client(url, client_session, start_listening_on_connect=False)

    await client.connect()

    assert client.connected


async def test_cannot_connect(client_session, url):
    """Test cannot connect."""
    client_session.ws_connect.side_effect = ClientError
    client = Client(url, client_session, start_listening_on_connect=False)

    with pytest.raises(CannotConnect):
        await client.connect()

    assert not client.connected


async def test_invalid_server_version(client_session, url, version_data):
    """Test client connect with invalid server version."""
    version_data["serverVersion"] = "invalid"
    client = Client(url, client_session, start_listening_on_connect=False)

    with pytest.raises(InvalidServerVersion):
        await client.connect()

    assert not client.connected
