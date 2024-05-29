"""Provide common pytest fixtures."""

import asyncio
from collections import deque
from copy import deepcopy
import json
from unittest.mock import AsyncMock, Mock, patch

from aiohttp import ClientSession, ClientWebSocketResponse
from aiohttp.http_websocket import WSMessage, WSMsgType
import pytest

from zwave_js_server.client import Client
from zwave_js_server.model.controller import Controller
from zwave_js_server.model.driver import Driver
from zwave_js_server.model.node import Node

from . import load_fixture

# pylint: disable=protected-access, unused-argument

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


@pytest.fixture(name="climate_radio_thermostat_ct100_plus_state", scope="session")
def climate_radio_thermostat_ct100_plus_state_fixture():
    """Load the radio thermostat node state fixture data."""
    return json.loads(load_fixture("climate_radio_thermostat_ct100_plus_state.json"))


@pytest.fixture(name="cover_qubino_shutter_state", scope="session")
def cover_qubino_shutter_state_fixture():
    """Load the qubino shutter cover node state fixture data."""
    return json.loads(load_fixture("cover_qubino_shutter_state.json"))


@pytest.fixture(name="idl_101_lock_state", scope="session")
def idl_101_lock_state_fixture():
    """Load the bad string meta data node state fixture data."""
    return json.loads(load_fixture("idl_101_lock_state.json"))


@pytest.fixture(name="wallmote_central_scene_state", scope="session")
def wallmote_central_scene_state_fixture():
    """Load the wallmote central scene node state fixture data."""
    return json.loads(load_fixture("wallmote_central_scene_state.json"))


@pytest.fixture(name="unparseable_json_string_value_state", scope="session")
def unparseable_json_string_value_state_fixture():
    """Load the unparseable string json value node state fixture data."""
    return json.loads(load_fixture("unparseable_json_string_value_state.json"))


@pytest.fixture(name="partial_and_full_parameter_state", scope="session")
def partial_and_full_parameter_state_fixture():
    """Load the node that has both partial and full parameters state fixture data."""
    return json.loads(load_fixture("partial_and_full_parameter_state.json"))


@pytest.fixture(name="invalid_multilevel_sensor_type_state", scope="session")
def invalid_multilevel_sensor_type_state_fixture():
    """Load the node that has an invalid multilevel sensor type state fixture data."""
    return json.loads(load_fixture("invalid_multilevel_sensor_type_state.json"))


@pytest.fixture(name="inovelli_switch_state", scope="session")
def inovelli_switch_state_fixture():
    """Load the bad string meta data node state fixture data."""
    return json.loads(load_fixture("inovelli_switch_state.json"))


@pytest.fixture(name="ring_keypad_state", scope="session")
def ring_keypad_state_fixture():
    """Load the ring keypad node state fixture data."""
    return json.loads(load_fixture("ring_keypad_state.json"))


@pytest.fixture(name="endpoints_with_command_classes_state", scope="session")
def endpoints_with_command_classes_state_fixture():
    """Load the node state fixture data with command classes on the endpoint."""
    return json.loads(load_fixture("endpoints_with_command_classes_state.json"))


@pytest.fixture(name="switch_enbrighten_zw3010_state", scope="session")
def switch_enbrighten_zw3010_state_fixture():
    """Load the enbrighten zw3010 switch node state fixture data."""
    return json.loads(load_fixture("switch_enbrighten_zw3010_state.json"))


@pytest.fixture(name="energy_production_state", scope="session")
def energy_production_state_fixture():
    """Load a mock node with energy production CC state fixture data."""
    return json.loads(load_fixture("energy_production_state.json"))


@pytest.fixture(name="lock_ultraloq_ubolt_pro_state", scope="session")
def lock_ultraloq_ubolt_pro_state_fixture():
    """Load the ultraloq U-Bolt Pro lock state fixture data."""
    return json.loads(load_fixture("lock_ultraloq_ubolt_pro_state.json"))


@pytest.fixture(name="client_session")
def client_session_fixture(ws_client):
    """Mock an aiohttp client session."""
    client_session = AsyncMock(spec_set=ClientSession)
    client_session.ws_connect.side_effect = AsyncMock(return_value=ws_client)
    return client_session


def create_ws_message(result):
    """Return a mock WSMessage."""
    message = Mock(spec_set=WSMessage)
    message.type = WSMsgType.TEXT
    message.data = json.dumps(result)
    message.json.return_value = result
    return message


@pytest.fixture(name="messages")
def messages_fixture():
    """Return a message buffer for the WS client."""
    return deque()


@pytest.fixture(name="ws_client")
async def ws_client_fixture(
    version_data,
    ws_message,
    result,
    messages,
    initialize_data,
    get_log_config_data,
):
    """Mock a websocket client.

    This fixture only allows a single message to be received.
    """
    ws_client = AsyncMock(spec_set=ClientWebSocketResponse, closed=False)
    ws_client.receive_json.side_effect = (
        version_data,
        initialize_data,
        get_log_config_data,
        result,
    )
    for data in (version_data, initialize_data, get_log_config_data, result):
        messages.append(create_ws_message(data))

    async def receive():
        """Return a websocket message."""
        await asyncio.sleep(0)

        try:
            message = messages.popleft()
        except IndexError:
            ws_client.closed = True
            return WSMessage(WSMsgType.CLOSED, None, None)

        return message

    ws_client.receive.side_effect = receive

    async def close_client(msg):
        """Close the client."""
        if msg["command"] in ("initialize", "start_listening"):
            return

        # We only want to skip for the initial call
        if (
            msg["command"] == "driver.get_log_config"
            and msg["messageId"] == "get-initial-log-config"
        ):
            return

        await asyncio.sleep(0)
        ws_client.closed = True

    ws_client.send_json.side_effect = close_client

    async def reset_close():
        """Reset the websocket client close method."""
        ws_client.closed = True

    ws_client.close.side_effect = reset_close

    return ws_client


@pytest.fixture(name="await_other")
async def await_other_fixture():
    """Await all other task but the current task."""

    async def wait_for_tasks(current_task):
        """Wait for the tasks."""
        tasks = asyncio.all_tasks() - {current_task}
        await asyncio.gather(*tasks)

    return wait_for_tasks


@pytest.fixture(name="driver_ready")
async def driver_ready_fixture():
    """Return an asyncio.Event for driver ready."""
    return asyncio.Event()


@pytest.fixture(name="version_data")
def version_data_fixture():
    """Return mock version data."""
    return {
        "type": "version",
        "driverVersion": "test_driver_version",
        "serverVersion": "test_server_version",
        "homeId": "test_home_id",
        "minSchemaVersion": 0,
        "maxSchemaVersion": 36,
    }


@pytest.fixture(name="initialize_data")
def initialize_data_fixture():
    """Return mock initialize data."""
    return {
        "type": "result",
        "success": True,
        "result": {},
        "messageId": "initialize",
    }


@pytest.fixture(name="log_config")
def log_config_fixture():
    """Return log config."""
    return {
        "enabled": True,
        "level": "info",
        "logToFile": False,
        "filename": "",
        "forceConsole": False,
    }


@pytest.fixture(name="get_log_config_data")
def get_log_config_data_fixture(log_config):
    """Return mock get_log_config data."""
    return {
        "type": "result",
        "success": True,
        "result": {"config": log_config},
        "messageId": "get-initial-log-config",
    }


@pytest.fixture(name="url")
def url_fixture():
    """Return a test url."""
    return TEST_URL


@pytest.fixture(name="result")
def result_fixture(controller_state, uuid4):
    """Return a server result message."""
    return {
        "type": "result",
        "success": True,
        "result": {"state": controller_state},
        "messageId": uuid4,
    }


@pytest.fixture(name="ws_message")
def ws_message_fixture(result):
    """Return a mock WSMessage."""
    return create_ws_message(result)


@pytest.fixture(name="uuid4")
def mock_uuid_fixture():
    """Patch uuid4."""
    uuid4_hex = "1234"
    with patch("uuid.uuid4") as uuid4:
        uuid4.return_value.hex = uuid4_hex
        yield uuid4_hex


@pytest.fixture(name="client")
async def client_fixture(client_session, ws_client, uuid4):
    """Return a client with a mock websocket transport.

    This fixture needs to be a coroutine function to get an event loop
    when creating the client.
    """
    client = Client("ws://test.org", client_session)
    client._client = ws_client
    return client


@pytest.fixture(name="mock_command")
def mock_command_fixture(ws_client, client, uuid4):
    """Mock a command and response."""
    mock_responses: list[tuple[dict, dict, bool]] = []
    ack_commands: list[dict] = []

    def apply_mock_command(
        match_command: dict, response: dict, success: bool = True
    ) -> list[dict]:
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
                    "success": success,
                }
                if success:
                    received_message["result"] = response
                else:
                    received_message.update(response)
                client._handle_incoming_message(received_message)
                return

        raise RuntimeError("Command not mocked!")

    ws_client.send_json.side_effect = set_response

    return apply_mock_command


@pytest.fixture(name="driver")
def driver_fixture(client, controller_state, log_config):
    """Return a driver instance with a supporting client."""
    client.driver = Driver(client, deepcopy(controller_state), log_config)
    return client.driver


@pytest.fixture(name="multisensor_6")
def multisensor_6_fixture(driver, multisensor_6_state):
    """Mock a multisensor 6 node."""
    node = Node(driver.client, deepcopy(multisensor_6_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="lock_schlage_be469")
def lock_schlage_be469_fixture(driver, lock_schlage_be469_state):
    """Mock a schlage lock node."""
    node = Node(driver.client, deepcopy(lock_schlage_be469_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="climate_radio_thermostat_ct100_plus")
def climate_radio_thermostat_ct100_plus_fixture(
    driver, climate_radio_thermostat_ct100_plus_state
):
    """Mock a radio thermostat node."""
    node = Node(driver.client, deepcopy(climate_radio_thermostat_ct100_plus_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="cover_qubino_shutter")
def cover_qubino_shutter_fixture(driver, cover_qubino_shutter_state):
    """Mock a qubino shutter cover node."""
    node = Node(driver.client, deepcopy(cover_qubino_shutter_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="wallmote_central_scene")
def wallmote_central_scene_fixture(driver, wallmote_central_scene_state):
    """Mock a wallmote central scene node."""
    node = Node(driver.client, deepcopy(wallmote_central_scene_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="controller")
def controller_fixture(driver, controller_state):
    """Return a controller instance with a supporting client."""
    controller = Controller(driver.client, deepcopy(controller_state))
    return controller


@pytest.fixture(name="inovelli_switch")
def inovelli_switch_fixture(driver, inovelli_switch_state):
    """Mock a inovelli switch node."""
    node = Node(driver.client, deepcopy(inovelli_switch_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="ring_keypad")
def ring_keypad_fixture(driver, ring_keypad_state):
    """Mock a ring keypad node."""
    node = Node(driver.client, deepcopy(ring_keypad_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="partial_and_full_parameter")
def partial_and_full_parameter_fixture(driver, partial_and_full_parameter_state):
    """Mock a node that has both partial and full parameters."""
    node = Node(driver.client, deepcopy(partial_and_full_parameter_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="invalid_multilevel_sensor_type")
def invalid_multilevel_sensor_type_fixture(
    driver, invalid_multilevel_sensor_type_state
):
    """Mock a node that has invalid multilevel sensor type."""
    node = Node(driver.client, deepcopy(invalid_multilevel_sensor_type_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="endpoints_with_command_classes")
def endpoints_with_command_classes_fixture(
    driver, endpoints_with_command_classes_state
):
    """Mock a node with command classes on an endpoint."""
    node = Node(driver.client, deepcopy(endpoints_with_command_classes_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="switch_enbrighten_zw3010")
def switch_enbrighten_zw3010_fixture(driver, switch_enbrighten_zw3010_state):
    """Mock an Enbrighten ZW3010 switch node."""
    node = Node(driver.client, deepcopy(switch_enbrighten_zw3010_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="energy_production")
def energy_prodution_fixture(driver, energy_production_state):
    """Mock a mock node with Energy Production CC."""
    node = Node(driver.client, deepcopy(energy_production_state))
    driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="lock_ultraloq_ubolt_pro")
def lock_ultraloq_ubolt_pro_fixture(driver, lock_ultraloq_ubolt_pro_state):
    """Mock an Ultraloq U-Bolt Pro lock node."""
    node = Node(driver.client, deepcopy(lock_ultraloq_ubolt_pro_state))
    driver.controller.nodes[node.node_id] = node
    return node
