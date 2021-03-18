"""Test the driver model."""
import json

from zwave_js_server.const import LogLevel
from zwave_js_server.event import Event
from zwave_js_server.model import driver as driver_pkg, log_config as log_config_pkg

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
    """Test update log config."""
    # Update log level
    ack_commands = mock_command(
        {"command": "update_log_config", "config": {"level": "error"}},
        {"success": True},
    )

    assert (
        await driver.async_update_log_config(
            log_config_pkg.LogConfig(level=LogLevel.ERROR)
        )
        is None
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "update_log_config",
        "config": {"level": "error"},
        "messageId": uuid4,
    }

    # Update all parameters
    ack_commands = mock_command(
        {
            "command": "update_log_config",
            "config": {
                "enabled": True,
                "level": "error",
                "logToFile": True,
                "filename": "/test.txt",
                "forceConsole": True,
            },
        },
        {"success": True},
    )
    assert (
        await driver.async_update_log_config(
            log_config_pkg.LogConfig(
                enabled=True,
                level=LogLevel.ERROR,
                log_to_file=True,
                filename="/test.txt",
                force_console=True,
            )
        )
        is None
    )

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "update_log_config",
        "config": {
            "enabled": True,
            "level": "error",
            "logToFile": True,
            "filename": "/test.txt",
            "forceConsole": True,
        },
        "messageId": uuid4,
    }


async def test_get_log_config(driver, uuid4, mock_command):
    """Test set value."""
    ack_commands = mock_command(
        {"command": "get_log_config"},
        {
            "success": True,
            "config": {
                "enabled": True,
                "level": "error",
                "logToFile": False,
                "filename": "/test.txt",
                "forceConsole": False,
            },
        },
    )
    log_config = await driver.async_get_log_config()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {"command": "get_log_config", "messageId": uuid4}

    assert log_config.enabled
    assert log_config.level == LogLevel.ERROR
    assert log_config.log_to_file is False
    assert log_config.filename == "/test.txt"
    assert log_config.force_console is False
