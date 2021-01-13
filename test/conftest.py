"""Provide common pytest fixtures."""
import json
from typing import List, Tuple

import pytest

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


class MockClient(Client):
    """Mock client."""

    def __init__(self):
        """Initialize mock client."""
        super().__init__("ws://test.org", None)
        self.state = STATE_CONNECTED
        self.mock_responses: List[Tuple[dict, dict]] = []
        self.mock_commands = []

    async def async_send_command(self, message):
        """Send a command and get a response."""
        for match_command, response in self.mock_responses:
            if all(message[key] == value for key, value in match_command.items()):
                self.mock_commands.append(message)
                return response

        raise RuntimeError("Command not mocked!")

    async def async_send_json_message(self, message):
        """Send JSON message."""
        raise RuntimeError("Method not mocked!")

    def mock_command(self, match_command: dict, response: dict):
        """Mock a command."""
        self.mock_responses.append((match_command, response))


@pytest.fixture(name="client")
async def client_fixture(loop):
    """Return a client with a mock websocket transport."""
    return MockClient()


@pytest.fixture(name="driver")
def driver_fixture(client, controller_state):
    """Return a driver instance with a supporting client."""
    return Driver(client, controller_state)


@pytest.fixture(name="node_multisensor_6")
def node_fixture(driver, multisensor_6_state):
    """Return a node instance with a supporting client."""
    node = Node(driver.client, multisensor_6_state)
    driver.controller.nodes[node.node_id] = node
    return node
