"""Test the client."""
import asyncio
from unittest.mock import AsyncMock

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


async def test_on_connect(client_session, url, await_other):
    """Test client on connect callback."""
    on_connect = AsyncMock()
    client = Client(url, client_session, start_listening_on_connect=False)
    client.register_on_connect(on_connect)

    await client.connect()
    await await_other(asyncio.current_task())

    assert client.connected
    on_connect.assert_awaited()


async def test_on_connect_exception(client_session, url, await_other, caplog):
    """Test client on connect callback."""
    on_connect_test = AsyncMock(side_effect=Exception("Boom"))
    client = Client(url, client_session, start_listening_on_connect=False)
    client.register_on_connect(on_connect_test)

    await client.connect()
    await await_other(asyncio.current_task())

    assert client.connected
    on_connect_test.assert_awaited()
    assert "Unexpected error in on_connect" in caplog.text
