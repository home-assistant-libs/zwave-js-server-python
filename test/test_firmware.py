"""Test for firmware functions."""

from zwave_js_server.firmware import (
    begin_firmware_update_guess_format,
    begin_firmware_update_known_format,
)


async def test_begin_firmware_update_guess_format(
    url, client_session, set_api_schema_data, multisensor_6, uuid4, mock_command
):
    """Test begin_firmware_update_guess_format."""
    node = multisensor_6
    mock_command(
        {"command": "set_api_schema"},
        set_api_schema_data,
    )
    ack_commands = mock_command(
        {"command": "node.begin_firmware_update_guess_format", "nodeId": node.node_id},
        {"result": "something"},
    )
    assert await begin_firmware_update_guess_format(
        url, node, "test", bytes(10), client_session
    ) == {"result": "something"}

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.begin_firmware_update_guess_format",
        "nodeId": node.node_id,
        "firmwareFilename": "test",
        "firmwareFile": "AAAAAAAAAAAAAA==",
        "messageId": uuid4,
    }


async def test_begin_firmware_update_known_format(
    url, client_session, set_api_schema_data, multisensor_6, uuid4, mock_command
):
    """Test begin_firmware_update_known_format."""
    node = multisensor_6
    mock_command(
        {"command": "set_api_schema"},
        set_api_schema_data,
    )
    ack_commands = mock_command(
        {"command": "node.begin_firmware_update_known_format", "nodeId": node.node_id},
        {"result": "something"},
    )
    assert await begin_firmware_update_known_format(
        url, node, "test", bytes(10), client_session
    ) == {"result": "something"}

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "node.begin_firmware_update_known_format",
        "nodeId": node.node_id,
        "firmwareFileFormat": "test",
        "firmwareFile": "AAAAAAAAAAAAAA==",
        "messageId": uuid4,
    }
