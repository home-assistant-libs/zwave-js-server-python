"""Test the server version helper."""
from unittest.mock import AsyncMock, call

from zwave_js_server.version import get_server_version


async def test_get_server_version(client_session, ws_client):
    """Test the get server version helper."""
    version_data = {
        "driverVersion": "test_driver_version",
        "serverVersion": "test_server_version",
        "homeId": "test_home_id",
    }
    client_session.ws_connect.side_effect = AsyncMock(return_value=ws_client)
    ws_client.receive_json.return_value = version_data
    url = "ws://test.org:3000"

    version_info = await get_server_version(url, client_session)

    assert client_session.ws_connect.called
    assert client_session.ws_connect.call_args == call(url)
    assert version_info.driver_version == version_data["driverVersion"]
    assert version_info.server_version == version_data["serverVersion"]
    assert version_info.home_id == version_data["homeId"]
    assert ws_client.close.called
