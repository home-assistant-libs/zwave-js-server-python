"""Test the server version helper."""
from unittest.mock import call

from zwave_js_server.version import get_server_version


async def test_get_server_version(client_session, ws_client, url, version_data):
    """Test the get server version helper."""
    ws_client.receive_json.return_value = version_data

    version_info = await get_server_version(url, client_session)

    assert client_session.ws_connect.called
    assert client_session.ws_connect.call_args == call(url)
    assert version_info.driver_version == version_data["driverVersion"]
    assert version_info.server_version == version_data["serverVersion"]
    assert version_info.home_id == version_data["homeId"]
    assert version_info.min_schema_version == version_data["minSchemaVersion"]
    assert version_info.max_schema_version == version_data["maxSchemaVersion"]
    assert ws_client.close.called


async def test_missing_server_schema_version(
    client_session, ws_client, url, version_data
):
    """test missing schema version processed as schema version 0."""
    del version_data["minSchemaVersion"]
    del version_data["maxSchemaVersion"]
    ws_client.receive_json.return_value = version_data
    version_info = await get_server_version(url, client_session)
    assert version_info.min_schema_version == 0
    assert version_info.max_schema_version == 0
    assert ws_client.close.called
