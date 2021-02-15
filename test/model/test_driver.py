"""Test the driver model."""
import json

from zwave_js_server.const import LogLevel
from zwave_js_server.event import Event
from zwave_js_server.model import driver as driver_pkg

from .. import load_fixture


def test_from_state():
    """Test from_state method."""
    ws_msgs = load_fixture("basic_dump.txt").strip().split("\n")

    driver = driver_pkg.Driver(None, json.loads(ws_msgs[0])["state"])

    for msg in ws_msgs[1:]:
        msg = json.loads(msg)
        assert msg["type"] == "event"
        event = Event(type=msg["event"]["event"], data=msg["event"])
        driver.receive_event(event)

    assert len(driver.controller.nodes) == 8


async def test_update_log_config(driver, uuid4, mock_command):
    """Test set value."""
    ack_commands = mock_command(
        {"command": "update_log_config", "config": {"logLevel": 0}},
        {"success": True},
    )
    assert await driver.async_update_log_config({"logLevel": LogLevel.ERROR})

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "update_log_config",
        "config": {"logLevel": 0},
        "messageId": uuid4,
    }
