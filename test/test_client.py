"""Test the client."""

import asyncio
from datetime import datetime
import logging
from unittest.mock import Mock, patch

from aiohttp.client_exceptions import ClientError, WSServerHandshakeError
from aiohttp.client_reqrep import ClientResponse, RequestInfo
from aiohttp.http_websocket import WSMsgType
import pytest

from test.common import MockCommandProtocol
from zwave_js_server.client import LOGGER, Client
from zwave_js_server.const import MAX_SERVER_SCHEMA_VERSION, LogLevel, __version__
from zwave_js_server.event import Event
from zwave_js_server.exceptions import (
    CannotConnect,
    ConnectionFailed,
    FailedCommand,
    FailedZWaveCommand,
    InvalidMessage,
    InvalidServerVersion,
    InvalidState,
    NotConnected,
)
from zwave_js_server.model.driver import Driver
from zwave_js_server.model.log_config import LogConfig


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


async def test_send_command_schema(
    client_session, url, ws_client, driver_ready, driver
):
    """Test sending unsupported command."""
    client = Client(url, client_session)
    await client.connect()
    assert client.connected
    client.driver = driver
    await client.listen(driver_ready)
    ws_client.receive.assert_awaited()

    # test schema version is at server maximum
    if client.version.max_schema_version < MAX_SERVER_SCHEMA_VERSION:
        assert client.schema_version == client.version.max_schema_version

    # send command of current schema version should not fail
    with pytest.raises(NotConnected):
        await client.async_send_command(
            {"command": "test"}, require_schema=client.schema_version
        )
    # send command of unsupported schema version should fail
    with pytest.raises(InvalidServerVersion):
        await client.async_send_command(
            {"command": "test"}, require_schema=client.schema_version + 2
        )
    with pytest.raises(InvalidServerVersion):
        await client.async_send_command_no_wait(
            {"command": "test"}, require_schema=client.schema_version + 2
        )


async def test_min_schema_version(client_session, url, version_data):
    """Test client connect with invalid schema version."""
    version_data["minSchemaVersion"] = 100
    client = Client(url, client_session)

    with pytest.raises(InvalidServerVersion):
        await client.connect()

    assert not client.connected


async def test_max_schema_version(client_session, url, version_data):
    """Test client connect with invalid schema version."""
    version_data["maxSchemaVersion"] = 0
    client = Client(url, client_session)

    with pytest.raises(InvalidServerVersion):
        await client.connect()

    assert not client.connected


async def test_send_json_when_disconnected(client_session, url):
    """Test send json message when disconnected."""
    client = Client(url, client_session)

    assert not client.connected

    with pytest.raises(NotConnected):
        await client.async_send_command({"test": None})


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
    client_session, url, ws_client, messages, ws_message, driver_ready
):
    """Test websocket error on listen."""
    client = Client(url, client_session)
    await client.connect()
    assert client.connected

    messages.append(ws_message)

    ws_client.receive.side_effect = asyncio.CancelledError()

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
    client_session, url, messages, ws_message, message_type, exception, driver_ready
):
    """Test different websocket message types that should raise on listen."""
    client = Client(url, client_session)
    await client.connect()
    assert client.connected

    ws_message.type = message_type
    messages.append(ws_message)

    with pytest.raises(exception):
        await client.listen(driver_ready)


@pytest.mark.parametrize(
    "message_type", [WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.CLOSING]
)
async def test_listen_disconnect_message_types(
    client_session, url, ws_client, messages, ws_message, message_type, driver_ready
):
    """Test different websocket message types that stop listen."""
    async with Client(url, client_session) as client:
        assert client.connected
        ws_message.type = message_type
        messages.append(ws_message)

        # This should break out of the listen loop before handling the received message.
        # Otherwise there will be an error.
        await client.listen(driver_ready)

    # Assert that we received a message.
    ws_client.receive.assert_awaited()


async def test_listen_invalid_message_data(
    client_session, url, messages, ws_message, driver_ready
):
    """Test websocket message data that should raise on listen."""
    client = Client(url, client_session)
    await client.connect()
    assert client.connected

    ws_message.json.side_effect = ValueError("Boom")
    messages.append(ws_message)

    with pytest.raises(InvalidMessage):
        await client.listen(driver_ready)


async def test_listen_not_success(client_session, url, result, driver_ready):
    """Test receive result message with success False on listen."""
    result["success"] = False
    result["errorCode"] = "error_code"
    result["message"] = "test"
    client = Client(url, client_session)
    await client.connect()

    with pytest.raises(FailedCommand):
        await client.listen(driver_ready)

    assert not client.connected


async def test_initialize_not_success(
    client_session, url, initialize_data, driver_ready
):
    """Test receive result message with success False on listen."""
    initialize_data["success"] = False
    initialize_data["errorCode"] = "error_code"
    initialize_data["message"] = "test"
    client = Client(url, client_session)
    await client.connect()

    with pytest.raises(FailedCommand):
        await client.listen(driver_ready)

    assert not client.connected


async def test_get_log_config_not_success(
    client_session, url, get_log_config_data, driver_ready
):
    """Test receive log config message with success False on listen."""
    get_log_config_data["success"] = False
    get_log_config_data["errorCode"] = "error_code"
    get_log_config_data["message"] = "test"
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
    client_session, url, ws_client, messages, ws_message, result, driver_ready
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
    messages.append(ws_message)

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


async def test_command_error_handling(client, mock_command):
    """Test error handling."""
    mock_command(
        {"command": "some_command"},
        {"errorCode": "unknown_command", "message": "test"},
        False,
    )

    with pytest.raises(FailedCommand) as raised:
        await client.async_send_command({"command": "some_command"})

    assert raised.value.error_code == "unknown_command"
    assert str(raised.value) == "unknown_command: test"

    mock_command(
        {"command": "some_zjs_command"},
        {
            "errorCode": "zwave_error",
            "zwaveErrorCode": 3,
            "zwaveErrorMessage": "Node 5 is dead",
        },
        False,
    )

    with pytest.raises(FailedZWaveCommand) as raised:
        await client.async_send_command({"command": "some_zjs_command"})

    assert raised.value.error_code == "zwave_error"
    assert raised.value.zwave_error_code == 3
    assert raised.value.zwave_error_message == "Node 5 is dead"


async def test_record_messages(client, wallmote_central_scene, mock_command, uuid4):
    """Test recording messages."""
    # pylint: disable=protected-access
    assert not client.recording_messages
    assert not client._recorded_commands
    assert not client._recorded_events
    client.begin_recording_messages()
    mock_command(
        {"command": "some_command"},
        {},
    )

    with pytest.raises(InvalidState):
        client.begin_recording_messages()

    with patch("zwave_js_server.client.datetime") as mock_dt:
        mock_dt.utcnow.return_value = datetime(2022, 1, 7, 1)

        await client.async_send_command({"command": "some_command"})

    assert len(client._recorded_commands) == 1
    assert len(client._recorded_events) == 0
    assert uuid4 in client._recorded_commands
    assert client._recorded_commands[uuid4]["record_type"] == "command"
    assert client._recorded_commands[uuid4]["command"] == "some_command"
    assert client._recorded_commands[uuid4]["command_msg"] == {
        "command": "some_command",
        "messageId": uuid4,
    }
    assert client._recorded_commands[uuid4]["result_msg"] == {
        "messageId": "1234",
        "result": {},
        "success": True,
        "type": "result",
    }
    assert "ts" in client._recorded_commands[uuid4]
    assert "result_ts" in client._recorded_commands[uuid4]

    with patch("zwave_js_server.client.datetime") as mock_dt:
        mock_dt.utcnow.return_value = datetime(2022, 1, 7, 0)
        client._handle_incoming_message(
            {
                "type": "event",
                "event": {
                    "source": "node",
                    "event": "value updated",
                    "nodeId": wallmote_central_scene.node_id,
                    "args": {
                        "commandClassName": "Binary Switch",
                        "commandClass": 39,
                        "endpoint": 0,
                        "property": "currentValue",
                        "newValue": False,
                        "prevValue": True,
                        "propertyName": "currentValue",
                    },
                },
            }
        )
    assert len(client._recorded_commands) == 1
    assert len(client._recorded_events) == 1
    logging.getLogger(__name__).error(client._recorded_events)
    event = client._recorded_events[0]
    assert event["record_type"] == "event"
    assert event["type"] == "value updated"
    assert event["event_msg"] == {
        "type": "event",
        "event": {
            "source": "node",
            "event": "value updated",
            "nodeId": wallmote_central_scene.node_id,
            "args": {
                "commandClassName": "Binary Switch",
                "commandClass": 39,
                "endpoint": 0,
                "property": "currentValue",
                "newValue": False,
                "prevValue": True,
                "propertyName": "currentValue",
            },
        },
    }
    assert "ts" in event

    replay_dump = client.end_recording_messages()

    assert len(replay_dump) == 2
    assert len(client._recorded_commands) == 0
    assert len(client._recorded_events) == 0

    # Testing that events are properly sorted by timestamp. Even though the event
    # comes after the command in the code, the patch should make the event appear first
    assert replay_dump[0]["record_type"] == "event"

    with pytest.raises(InvalidState):
        client.end_recording_messages()


async def test_additional_user_agent_components(client_session, url):
    """Test additionalUserAgentComponents parameter."""
    # pylint: disable=protected-access
    client = Client(
        url, client_session, additional_user_agent_components={"foo": "bar"}
    )
    client._client = True
    with (
        patch(
            "zwave_js_server.client.Client._send_json_message", return_value=None
        ) as send_json_mock,
        patch(
            "zwave_js_server.client.Client._receive_json_or_raise",
            return_value={"success": True},
        ),
    ):
        await client.initialize()
        send_json_mock.assert_called_once_with(
            {
                "command": "initialize",
                "messageId": "initialize",
                "schemaVersion": 44,
                "additionalUserAgentComponents": {
                    "zwave-js-server-python": __version__,
                    "foo": "bar",
                },
            }
        )


async def test_pop_future_none(client_session, url, driver_ready):
    """Test when a future has been cleared from futures dict, popping still works."""
    client = Client(url, client_session)
    await client.connect()

    assert client.connected

    asyncio.create_task(client.listen(driver_ready))

    await driver_ready.wait()

    with pytest.raises(asyncio.CancelledError):
        await client.async_send_command({"command": "some_command"})


async def test_log_server(
    client: Client,
    driver: Driver,
    caplog: pytest.LogCaptureFixture,
    mock_command: MockCommandProtocol,
) -> None:
    """Test logging from server."""
    # pylint: disable=protected-access
    assert client.connected
    mock_command(
        {"command": "start_listening_logs"},
        {},
    )
    mock_command(
        {"command": "stop_listening_logs"},
        {},
    )
    # Set log levels to force the lib to change log levels
    LOGGER.setLevel(logging.INFO)
    client.driver.log_config = LogConfig(True, LogLevel.DEBUG, False, None, None)
    await client.enable_server_logging()
    assert client.server_logging_enabled
    assert len(caplog.records) == 2
    assert "logging is currently more verbose" in caplog.records[0].message
    assert caplog.records[0].name == "zwave_js_server"

    # Test that enabling again is a no-op
    await client.enable_server_logging()
    assert client.server_logging_enabled
    assert len(caplog.records) == 2

    LOGGER.setLevel(logging.INFO)
    event = Event(
        "log config updated",
        data={
            "source": "driver",
            "event": "log config updated",
            "config": {"level": "silly"},
        },
    )
    driver.receive_event(event)

    assert len(caplog.records) == 3
    assert "logging is currently more verbose" in caplog.records[2].message
    assert caplog.records[2].name == "zwave_js_server"

    event = Event(
        type="logging",
        data={
            "source": "driver",
            "event": "logging",
            "formattedMessage": [
                "2021-04-18T18:03:34.051Z CNTRLR   [Node 005] [~] \n",
                "test",
            ],
            "level": "debug",
            "primaryTags": "[Node 005] [~] [Notification]",
            "secondaryTags": "[Endpoint 0]",
            "message": "Home Security[Motion sensor status]\n: 8 => 0",
            "direction": "  ",
            "label": "CNTRLR",
            "timestamp": "2021-04-18T18:03:34.051Z",
            "multiline": True,
            "secondaryTagPadding": -1,
            "context": {
                "source": "controller",
                "type": "node",
                "nodeId": 5,
                "header": "Notification",
                "direction": "none",
                "change": "notification",
                "endpoint": 0,
            },
        },
    )
    driver.receive_event(event)
    assert len(caplog.records) == 4
    assert "Node 005" in caplog.records[3].message
    assert caplog.records[3].levelno == logging.DEBUG
    assert caplog.records[3].name == "zwave_js_server.server"

    # First time we disable should be clean
    client.disable_server_logging()
    assert not client.server_logging_enabled
    assert len(caplog.records) == 4

    # Test that disabling again is a no-op
    client.disable_server_logging()
    assert not client.server_logging_enabled

    # Test that enabling server logging raises an error when client is not connected
    client.driver = None
    client._client = None

    with pytest.raises(InvalidState):
        await client.enable_server_logging()

    client.disable_server_logging()
