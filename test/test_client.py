"""Test the client."""
import asyncio
from unittest.mock import Mock

import pytest
from aiohttp.client_exceptions import ClientError, WSServerHandshakeError
from aiohttp.client_reqrep import ClientResponse, RequestInfo
from aiohttp.http_websocket import WSMsgType

from zwave_js_server.client import Client
from zwave_js_server.exceptions import (
    CannotConnect,
    ConnectionFailed,
    FailedCommand,
    InvalidMessage,
    InvalidServerVersion,
    InvalidState,
    NotConnected,
)

# pylint: disable=too-many-arguments


async def test_connect_disconnect(client_session, url):
    """Test client connect and disconnect."""
    async with Client(url, client_session) as client:
        assert client.connected

    assert not client.connected


@pytest.mark.parametrize(
    "error",
    [ClientError, WSServerHandshakeError(Mock(RequestInfo), (Mock(ClientResponse),))],
)
async def test_cannot_connect(client_session, url, error):
    """Test cannot connect."""
    client_session.ws_connect.side_effect = error
    client = Client(url, client_session)

    with pytest.raises(CannotConnect):
        await client.connect()

    assert not client.connected


async def test_invalid_server_version(client_session, url, version_data, caplog):
    """Test client connect with invalid server version."""
    version_data["serverVersion"] = "invalid"
    client = Client(url, client_session)

    with pytest.raises(InvalidServerVersion):
        await client.connect()

    assert not client.connected


async def test_newer_server_version(client_session, url, version_data, caplog):
    """Test client connect with invalid server version."""
    version_data["serverVersion"] = "99999.0.0"
    client = Client(url, client_session)

    await client.connect()

    assert client.connected
    assert "Connected to a Zwave JS Server with an untested version" in caplog.text


async def test_send_json_when_disconnected(client_session, url):
    """Test send json message when disconnected."""
    client = Client(url, client_session)

    assert not client.connected

    with pytest.raises(NotConnected):
        await client._send_json_message({"test": None})


async def test_listen(client_session, url, driver_ready):
    """Test client listen."""
    client = Client(url, client_session)

    assert not client.driver

    await client.connect()

    assert client.connected

    asyncio.create_task(client.listen(driver_ready))
    await driver_ready.wait()
    assert client.driver

    await client.disconnect()
    assert not client.connected


async def test_listen_client_error(
    client_session, url, ws_client, ws_message, driver_ready
):
    """Test websocket error on listen."""
    client = Client(url, client_session)
    await client.connect()
    assert client.connected

    ws_client.receive.side_effect = asyncio.CancelledError()
    ws_message.reset_mock()
    ws_client.closed = False

    # This should break out of the listen loop before any message is received.
    with pytest.raises(asyncio.CancelledError):
        await client.listen(driver_ready)

    assert not ws_message.json.called


@pytest.mark.parametrize(
    "message_type, exception",
    [
        (WSMsgType.ERROR, ConnectionFailed),
        (WSMsgType.BINARY, InvalidMessage),
    ],
)
async def test_listen_error_message_types(
    client_session, url, ws_client, ws_message, message_type, exception, driver_ready
):
    """Test different websocket message types that should raise on listen."""
    client = Client(url, client_session)
    await client.connect()
    assert client.connected

    ws_message.type = message_type
    ws_client.closed = False

    with pytest.raises(exception):
        await client.listen(driver_ready)


@pytest.mark.parametrize("message_type", [WSMsgType.CLOSED, WSMsgType.CLOSING])
async def test_listen_disconnect_message_types(
    client_session, url, ws_client, ws_message, message_type, driver_ready, await_other
):
    """Test different websocket message types that stop listen."""
    async with Client(url, client_session) as client:
        assert client.connected
        ws_message.type = message_type

        # This should break out of the listen loop before handling the received message.
        # Otherwise there will be an error.
        await client.listen(driver_ready)

    # Assert that we received a message.
    ws_client.receive.assert_awaited()


async def test_listen_invalid_message_data(
    client_session, url, ws_client, ws_message, driver_ready
):
    """Test websocket message data that should raise on listen."""
    client = Client(url, client_session)
    await client.connect()
    assert client.connected

    ws_message.json.side_effect = ValueError("Boom")
    ws_client.closed = False

    with pytest.raises(InvalidMessage):
        await client.listen(driver_ready)


async def test_listen_not_success(client_session, url, result, driver_ready):
    """Test receive result message with success False on listen."""
    result["success"] = False
    result["errorCode"] = "error_code"
    client = Client(url, client_session)
    await client.connect()

    with pytest.raises(FailedCommand):
        await client.listen(driver_ready)

    assert not client.connected


async def test_listen_without_connect(client_session, url, driver_ready):
    """Test listen without first being connected."""
    client = Client(url, client_session)
    assert not client.connected

    with pytest.raises(InvalidState):
        await client.listen(driver_ready)


async def test_listen_event(
    client_session, url, ws_client, ws_message, result, driver_ready, await_other
):
    """Test receiving event result type on listen."""
    client = Client(url, client_session)
    await client.connect()

    assert client.connected

    result["type"] = "event"
    result["event"] = {
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

    await client.listen(driver_ready)
    ws_client.receive.assert_awaited()


async def test_listen_unknown_result_type(
    client_session, url, ws_client, result, driver_ready, driver
):
    """Test websocket message with unknown type on listen."""
    client = Client(url, client_session)
    await client.connect()

    assert client.connected

    # Make sure there's a driver so we can test an unknown event.
    client.driver = driver
    result["type"] = "unknown"

    # Receiving an unknown message type should not error.
    await client.listen(driver_ready)

    ws_client.receive.assert_awaited()
