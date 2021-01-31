"""Test the client."""
import asyncio
from unittest.mock import AsyncMock, Mock

from aiohttp.client_exceptions import ClientError, WSServerHandshakeError
from aiohttp.client_reqrep import ClientResponse, RequestInfo
from aiohttp.http_websocket import WSMsgType
import pytest

from zwave_js_server.client import Client
from zwave_js_server.exceptions import (
    CannotConnect,
    ConnectionFailed,
    InvalidMessage,
    InvalidServerVersion,
    NotConnected,
)


async def test_connect(client_session, url):
    """Test client connect."""
    client = Client(url, client_session, start_listening_on_connect=False)

    await client.connect()

    assert client.connected


@pytest.mark.parametrize(
    "error",
    [ClientError, WSServerHandshakeError(Mock(RequestInfo), (Mock(ClientResponse),))],
)
async def test_cannot_connect(client_session, url, error):
    """Test cannot connect."""
    client_session.ws_connect.side_effect = error
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


async def test_send_json_when_disconnected(client_session, url):
    """Test send json message when disconnected."""
    client = Client(url, client_session, start_listening_on_connect=False)

    assert not client.connected

    with pytest.raises(NotConnected):
        await client.async_send_json_message({"test": None})


async def test_on_connect_on_disconnect(client_session, url, await_other):
    """Test client on connect and on disconnect callback."""
    on_connect = AsyncMock()
    on_disconnect = AsyncMock()
    client = Client(url, client_session, start_listening_on_connect=False)
    unsubscribe_on_connect = client.register_on_connect(on_connect)
    unsubscribe_on_disconnect = client.register_on_disconnect(on_disconnect)

    await client.connect()
    await await_other(asyncio.current_task())

    assert client.connected
    on_connect.assert_awaited()

    on_connect.reset_mock()

    await client.disconnect()
    await await_other(asyncio.current_task())

    assert not client.connected
    on_disconnect.assert_awaited()

    on_disconnect.reset_mock()

    unsubscribe_on_connect()
    unsubscribe_on_disconnect()
    await client.connect()
    await await_other(asyncio.current_task())

    assert client.connected
    on_connect.assert_not_awaited()

    await client.disconnect()
    await await_other(asyncio.current_task())

    assert not client.connected
    on_disconnect.assert_not_awaited()


async def test_on_connect_exception(client_session, url, await_other, caplog):
    """Test client on connect callback."""
    on_connect = AsyncMock(side_effect=Exception("Boom"))
    client = Client(url, client_session, start_listening_on_connect=False)
    client.register_on_connect(on_connect)

    await client.connect()
    await await_other(asyncio.current_task())

    assert client.connected
    on_connect.assert_awaited()
    assert "Unexpected error in on_connect" in caplog.text


async def test_listen(client_session, url, await_other):
    """Test client listen."""
    on_initialization = AsyncMock()
    client = Client(url, client_session, start_listening_on_connect=True)
    unsubscribe_on_initialization = client.register_on_initialized(on_initialization)

    assert not client.driver

    await client.connect()
    await client.listen()
    await await_other(asyncio.current_task())

    assert client.connected
    assert client.driver
    on_initialization.assert_awaited()

    on_initialization.reset_mock()

    await client.disconnect()
    await await_other(asyncio.current_task())

    assert not client.connected

    unsubscribe_on_initialization()
    await client.connect()
    await client.listen()
    await await_other(asyncio.current_task())

    assert client.connected
    on_initialization.assert_not_awaited()


@pytest.mark.parametrize(
    "error",
    [ClientError, WSServerHandshakeError(Mock(RequestInfo), (Mock(ClientResponse),))],
)
async def test_listen_client_error(client_session, url, ws_client, error):
    """Test websocket error on listen."""
    client = Client(url, client_session, start_listening_on_connect=True)
    await client.connect()

    ws_client.receive.side_effect = error

    with pytest.raises(ConnectionFailed):
        await client.listen()


@pytest.mark.parametrize(
    "message_type, exception",
    [(WSMsgType.ERROR, ConnectionFailed), (WSMsgType.BINARY, InvalidMessage)],
)
async def test_listen_error_message_types(
    client_session, url, ws_message, message_type, exception
):
    """Test different websocket message types that should raise on listen."""
    client = Client(url, client_session, start_listening_on_connect=True)
    await client.connect()

    ws_message.type = message_type

    with pytest.raises(exception):
        await client.listen()


@pytest.mark.parametrize("message_type", [WSMsgType.CLOSED, WSMsgType.CLOSING])
async def test_listen_disconnect_message_types(
    client_session, url, ws_client, ws_message, message_type
):
    """Test different websocket message types that stop listen."""
    ws_message.type = message_type

    # This should break out of the listen loop before handling the received message.
    # Otherwise there will be an error.
    async with Client(url, client_session, start_listening_on_connect=True) as client:
        await client.listen()

    # Assert that we received a message.
    ws_client.receive.assert_awaited()
