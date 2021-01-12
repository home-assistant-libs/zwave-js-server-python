"""Provide common pytest fixtures."""
import json
from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientSession, ClientWebSocketResponse

from zwave_js_server.client import STATE_CONNECTED, Client
from zwave_js_server.model.driver import Driver
from zwave_js_server.model.node import Node

from . import load_fixture


@pytest.fixture(name="controller_state", scope="session")
def controller_state_fixture():
    """Load the controller state fixture data."""
    return json.loads(load_fixture("controller_state.json"))


@pytest.fixture(name="multisensor_6_state", scope="session")
def multisensor_6_state_fixture():
    """Load the multisensor 6 node state fixture data."""
    return json.loads(load_fixture("multisensor_6_state.json"))


@pytest.fixture(name="client_session")
def client_session_fixture():
    """Mock an aiohttp client session."""
    return AsyncMock(spec_set=ClientSession)


@pytest.fixture(name="ws_client")
def ws_client_fixture():
    """Mock a websocket client."""
    return AsyncMock(spec_set=ClientWebSocketResponse)


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
    client_session.ws_connect.return_value = ws_client
    client = Client("ws://test.org", client_session)
    client.state = STATE_CONNECTED
    client.client = ws_client
    return client


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
