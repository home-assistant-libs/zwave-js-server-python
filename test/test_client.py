"""Test the client."""
import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp.client_exceptions import ClientError, WSServerHandshakeError
from aiohttp.client_reqrep import ClientResponse, RequestInfo
from aiohttp.http_websocket import WSMsgType

from zwave_js_server.client import Client
from zwave_js_server.exceptions import (
    CannotConnect,
    ConnectionFailed,
    InvalidMessage,
    InvalidServerVersion,
    InvalidState,
    NotConnected,
)

# pylint: disable=too-many-arguments


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


async def test_listen_invalid_message_data(client_session, url, ws_message):
    """Test websocket message data that should raise on listen."""
    client = Client(url, client_session, start_listening_on_connect=True)
    await client.connect()

    ws_message.json.side_effect = ValueError("Boom")

    with pytest.raises(InvalidMessage):
        await client.listen()


async def test_listen_invalid_state(client_session, url, result):
    """Test missing driver state on listen."""
    result["type"] = "event"
    result["event"] = {
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
        }
    }
    client = Client(url, client_session, start_listening_on_connect=True)
    await client.connect()

    with pytest.raises(InvalidState):
        await client.listen()


async def test_listen_unknown_result_type(
    client_session, url, ws_client, ws_message, result, await_other
):
    """Test websocket message with unknown result on listen."""
    client = Client(url, client_session, start_listening_on_connect=True)
    await client.connect()
    await client.listen()
    await await_other(asyncio.current_task())

    assert client.connected
    assert client.driver

    ws_client.receive.reset_mock()
    ws_client.closed = False

    async def receive():
        """Return a websocket message."""
        ws_client.closed = True
        return ws_message

    ws_client.receive.side_effect = receive
    result["type"] = "unknown"

    # Receiving an unknown result type should not error.
    await client.listen()

    ws_client.receive.assert_awaited()
