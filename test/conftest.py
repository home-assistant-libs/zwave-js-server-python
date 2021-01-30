"""Provide common pytest fixtures."""
import asyncio
import json
from typing import List, Tuple
from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientSession, ClientWebSocketResponse

from zwave_js_server.client import STATE_CONNECTED, Client
from zwave_js_server.const import MIN_SERVER_VERSION
from zwave_js_server.model.controller import Controller
from zwave_js_server.model.driver import Driver
from zwave_js_server.model.node import Node

from . import load_fixture

# pylint: disable=unused-argument

TEST_URL = "ws://test.org:3000"


@pytest.fixture(name="controller_state", scope="session")
def controller_state_fixture():
    """Load the controller state fixture data."""
    return json.loads(load_fixture("controller_state.json"))


@pytest.fixture(name="multisensor_6_state", scope="session")
def multisensor_6_state_fixture():
    """Load the multisensor 6 node state fixture data."""
    return json.loads(load_fixture("multisensor_6_state.json"))


@pytest.fixture(name="lock_schlage_be469_state", scope="session")
def lock_schlage_be469_state_fixture():
    """Load the schlage lock node state fixture data."""
    return json.loads(load_fixture("lock_schlage_be469_state.json"))


@pytest.fixture(name="client_session")
def client_session_fixture(ws_client):
    """Mock an aiohttp client session."""
    client_session = AsyncMock(spec_set=ClientSession)
    client_session.ws_connect.side_effect = AsyncMock(return_value=ws_client)
    return client_session


@pytest.fixture(name="ws_client")
def ws_client_fixture(version_data):
    """Mock a websocket client."""
    ws_client = AsyncMock(spec_set=ClientWebSocketResponse)
    ws_client.receive_json.return_value = version_data
    return ws_client


@pytest.fixture(name="version_data")
def version_data_fixture():
    """Return mock version data."""
    return {
        "driverVersion": "test_driver_version",
        "serverVersion": MIN_SERVER_VERSION,
        "homeId": "test_home_id",
    }


@pytest.fixture(name="url")
def url_fixture():
    """Return a test url."""
    return TEST_URL


@pytest.fixture(name="uuid4")
def mock_uuid_fixture():
    """Patch uuid4."""
    uuid4_hex = "1234"
    with patch("uuid.uuid4") as uuid4:
        uuid4.return_value.hex = uuid4_hex
        yield uuid4_hex


@pytest.fixture(name="client")
async def client_fixture(loop, client_session, ws_client, uuid4):
    """Return a client with a mock websocket transport.

    This fixture needs to be a coroutine function to get an event loop
    when creating the client.
    """
    client = Client("ws://test.org", client_session)
    client.state = STATE_CONNECTED
    client.client = ws_client
    return client


@pytest.fixture(name="await_other")
async def await_other_fixture(loop):
    """Await all tasks except the current task."""

    async def wait_for_tasks(current_task):
        """Await the tasks."""
        tasks = asyncio.all_tasks() - {current_task}
        await asyncio.gather(*tasks)

    return wait_for_tasks


@pytest.fixture(name="mock_command")
def mock_command_fixture(ws_client, client, uuid4):
    """Mock a command and response."""
    mock_responses: List[Tuple[dict, dict, bool]] = []
    ack_commands: List[dict] = []

    def apply_mock_command(
        match_command: dict, response: dict, success: bool = True
    ) -> List[dict]:
        """Apply the mock command and response return value to the transport.

        Return the list with correctly acknowledged commands.
        """
        mock_responses.append((match_command, response, success))
        return ack_commands

    async def set_response(message):
        """Check the message and set the mocked response if a command matches."""
        for match_command, response, success in mock_responses:
            if all(message[key] == value for key, value in match_command.items()):
                ack_commands.append(message)
                received_message = {
                    "type": "result",
                    "messageId": uuid4,
                    "result": response,
                    "success": success,
                }
                client.async_handle_message(received_message)
                return

        raise RuntimeError("Command not mocked!")

    ws_client.send_json.side_effect = set_response

    return apply_mock_command


@pytest.fixture(name="driver")
def driver_fixture(client, controller_state):
    """Return a driver instance with a supporting client."""
    return Driver(client, controller_state)


@pytest.fixture(name="node")
def node_fixture(driver, multisensor_6_state):
    """Return a node instance with a supporting client."""
    node = Node(driver.client, multisensor_6_state)
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="lock_schlage_be469")
def lock_schlage_be469_fixture(driver, lock_schlage_be469_state):
    """Mock a schlage lock node."""
    node = Node(driver.client, lock_schlage_be469_state)
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="controller")
def controller_fixture(driver, controller_state):
    """Return a controller instance with a supporting client."""
    controller = Controller(driver.client, controller_state)
    return controller
