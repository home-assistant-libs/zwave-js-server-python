"""Test the CLI in main."""
import sys
from unittest.mock import AsyncMock, patch

import pytest

from zwave_js_server.__main__ import main
from zwave_js_server.const import MIN_SERVER_VERSION

# pylint: disable=unused-argument


@pytest.fixture(name="client_session")
def client_session_fixture(ws_client):
    """Mock the aiohttp client session."""
    with patch("aiohttp.ClientSession") as session:
        session.return_value.__aenter__.return_value.ws_connect.side_effect = AsyncMock(
            return_value=ws_client
        )
        yield session


def test_server_version(client_session, url, ws_client, result, capsys):
    """Test print server version."""
    with patch.object(
        sys, "argv", ["zwave_js_server", url, "--server-version"]
    ), pytest.raises(SystemExit) as sys_exit:
        main()

    assert sys_exit.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == (
        "Driver: test_driver_version\n"
        f"Server: {MIN_SERVER_VERSION}\n"
        "Home ID: test_home_id\n"
    )
    assert ws_client.receive_json.call_count == 1
    assert ws_client.close.call_count == 1


@pytest.mark.parametrize("result", ["test_result"])
def test_dump_state(client_session, url, ws_client, result, capsys):
    """Test dump state."""
    with patch.object(
        sys, "argv", ["zwave_js_server", url, "--dump-state"]
    ), pytest.raises(SystemExit) as sys_exit:
        main()

    assert sys_exit.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == (
        "{'type': 'version', 'driverVersion': 'test_driver_version', "
        f"'serverVersion': '{MIN_SERVER_VERSION}', 'homeId': 'test_home_id'}}\n"
        "test_result\n"
    )
    assert ws_client.receive_json.call_count == 2
    assert ws_client.close.call_count == 1


def test_connect(client_session, url, ws_client):
    """Test connect."""
    with patch.object(sys, "argv", ["zwave_js_server", url]), pytest.raises(
        SystemExit
    ) as sys_exit:
        main()

    assert sys_exit.value.code == 0
    assert ws_client.receive.call_count == 2
