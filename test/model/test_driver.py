"""Test the driver model."""

import json

import pytest

from zwave_js_server.const import LogLevel
from zwave_js_server.event import Event
from zwave_js_server.model import (
    driver as driver_pkg,
    log_config as log_config_pkg,
    log_message as log_message_pkg,
)
from zwave_js_server.model.driver.firmware import DriverFirmwareUpdateStatus

from .. import load_fixture


def test_from_state(client, log_config):
    """Test from_state method."""
    ws_msgs = load_fixture("basic_dump.txt").strip().split("\n")

    driver = driver_pkg.Driver(
        client, json.loads(ws_msgs[0])["result"]["state"], log_config
    )
    assert driver == driver_pkg.Driver(
        client, json.loads(ws_msgs[0])["result"]["state"], log_config
    )
    assert driver != driver.controller.home_id
    assert hash(driver) == hash(driver.controller.home_id)

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
        {"command": "driver.update_log_config", "config": {"level": "error"}},
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
        "command": "driver.update_log_config",
        "config": {"level": "error"},
        "messageId": uuid4,
    }

    # Update all parameters
    ack_commands = mock_command(
        {
            "command": "driver.update_log_config",
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
        "command": "driver.update_log_config",
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
        {"command": "driver.get_log_config"},
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
    assert ack_commands[0] == {"command": "driver.get_log_config", "messageId": uuid4}

    assert log_config.enabled
    assert log_config.level == LogLevel.ERROR
    assert log_config.log_to_file is False
    assert log_config.filename == "/test.txt"
    assert log_config.force_console is False


async def test_listening_logs(client, driver, uuid4, mock_command):
    """Test listening to logs helpers."""
    # Test that start listening to logs command is sent
    ack_commands = mock_command(
        {"command": "start_listening_logs"},
        {"success": True},
    )
    await client.async_start_listening_logs()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "start_listening_logs",
        "messageId": uuid4,
    }

    # Test that stop listening to logs command is sent
    ack_commands = mock_command(
        {"command": "stop_listening_logs"},
        {"success": True},
    )
    await client.async_stop_listening_logs()

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "stop_listening_logs",
        "messageId": uuid4,
    }

    # Test receiving a log message event
    event = Event(
        type="logging",
        data={
            "source": "driver",
            "event": "logging",
            "formattedMessage": [
                "2021-04-18T18:03:34.051Z CNTRLR   [Node 005] [~] \n",
                "test",
            ],
            "level": "debug",
            "primaryTags": "[Node 005] [~] [Notification]",
            "secondaryTags": "[Endpoint 0]",
            "message": "Home Security[Motion sensor status]\n: 8 => 0",
            "direction": "  ",
            "label": "CNTRLR",
            "timestamp": "2021-04-18T18:03:34.051Z",
            "multiline": True,
            "secondaryTagPadding": -1,
            "context": {
                "source": "controller",
                "type": "node",
                "nodeId": 5,
                "header": "Notification",
                "direction": "none",
                "change": "notification",
                "endpoint": 0,
            },
        },
    )
    driver.receive_event(event)
    assert "log_message" in event.data
    assert isinstance(event.data["log_message"], log_message_pkg.LogMessage)
    log_message = event.data["log_message"]
    assert log_message.message == ["Home Security[Motion sensor status]", ": 8 => 0"]
    assert log_message.formatted_message == [
        "2021-04-18T18:03:34.051Z CNTRLR   [Node 005] [~] ",
        "test",
    ]
    assert log_message.direction == "  "
    assert log_message.primary_tags == "[Node 005] [~] [Notification]"
    assert log_message.secondary_tags == "[Endpoint 0]"
    assert log_message.level == "debug"
    assert log_message.label == "CNTRLR"
    assert log_message.multiline
    assert log_message.secondary_tag_padding == -1
    assert log_message.timestamp == "2021-04-18T18:03:34.051Z"

    context = log_message.context
    assert context.change == "notification"
    assert context.direction == "none"
    assert context.endpoint == 0
    assert context.header == "Notification"
    assert context.node_id == 5
    assert context.source == "controller"
    assert context.type == "node"
    assert context.internal is None
    assert context.property_ is None
    assert context.property_key is None
    assert context.command_class is None


async def test_statistics(driver, uuid4, mock_command):
    """Test statistics commands."""
    # Test that enable_statistics command is sent
    ack_commands = mock_command(
        {
            "command": "driver.enable_statistics",
            "applicationName": "test_name",
            "applicationVersion": "test_version",
        },
        {"success": True},
    )
    await driver.async_enable_statistics("test_name", "test_version")

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "driver.enable_statistics",
        "applicationName": "test_name",
        "applicationVersion": "test_version",
        "messageId": uuid4,
    }

    # Test that disable_statistics command is sent
    ack_commands = mock_command(
        {"command": "driver.disable_statistics"},
        {"success": True},
    )
    await driver.async_disable_statistics()

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "driver.disable_statistics",
        "messageId": uuid4,
    }

    # Test that is statistics_enabled command is sent
    ack_commands = mock_command(
        {"command": "driver.is_statistics_enabled"},
        {"success": True, "statisticsEnabled": True},
    )
    assert await driver.async_is_statistics_enabled()

    assert len(ack_commands) == 3
    assert ack_commands[2] == {
        "command": "driver.is_statistics_enabled",
        "messageId": uuid4,
    }


async def test_log_config_updated(driver):
    """Test the log_config_updated event."""
    # Modify current log config in an update and assert that it changed
    assert driver.log_config.level != LogLevel.SILLY
    log_config = driver.log_config.to_dict()
    log_config["level"] = "silly"
    event = Event(
        "log config updated",
        data={"source": "driver", "event": "log config updated", "config": log_config},
    )
    driver.receive_event(event)
    assert driver.log_config.level == LogLevel.SILLY


async def test_check_for_config_updates(driver, uuid4, mock_command):
    """Test driver.check_for_config_updates command."""
    ack_commands = mock_command(
        {"command": "driver.check_for_config_updates"},
        {"updateAvailable": False, "installedVersion": "1.0.0"},
    )

    check_config_updates = await driver.async_check_for_config_updates()
    assert check_config_updates.installed_version == "1.0.0"
    assert check_config_updates.update_available is False
    assert check_config_updates.new_version is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "driver.check_for_config_updates",
        "messageId": uuid4,
    }


async def test_install_config_update(driver, uuid4, mock_command):
    """Test driver.install_config_update command."""
    ack_commands = mock_command(
        {"command": "driver.install_config_update"},
        {"success": False},
    )

    assert not await driver.async_install_config_update()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "driver.install_config_update",
        "messageId": uuid4,
    }


async def test_set_preferred_scales(driver, uuid4, mock_command):
    """Test driver.set_preferred_scales command."""
    ack_commands = mock_command({"command": "driver.set_preferred_scales"}, {})

    assert not await driver.async_set_preferred_scales({1: 1})

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "driver.set_preferred_scales",
        "scales": {1: 1},
        "messageId": uuid4,
    }


async def test_hard_reset(driver, uuid4, mock_command):
    """Test driver hard reset command."""
    ack_commands = mock_command({"command": "driver.hard_reset"}, {})

    assert not await driver.async_hard_reset()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "driver.hard_reset",
        "messageId": uuid4,
    }


async def test_try_soft_reset(driver, uuid4, mock_command):
    """Test driver try soft reset command."""
    ack_commands = mock_command({"command": "driver.try_soft_reset"}, {})

    assert not await driver.async_try_soft_reset()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "driver.try_soft_reset",
        "messageId": uuid4,
    }


async def test_soft_reset(driver, uuid4, mock_command):
    """Test driver soft reset command."""
    ack_commands = mock_command({"command": "driver.soft_reset"}, {})

    assert not await driver.async_soft_reset()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "driver.soft_reset",
        "messageId": uuid4,
    }


async def test_shutdown(driver, uuid4, mock_command):
    """Test driver shutdown command."""
    ack_commands = mock_command({"command": "driver.shutdown"}, {"success": True})

    assert await driver.async_shutdown()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "driver.shutdown",
        "messageId": uuid4,
    }


async def test_unknown_event(driver):
    """Test that an unknown event type causes an exception."""
    with pytest.raises(KeyError):
        assert driver.receive_event(Event("unknown_event", {"source": "driver"}))


async def test_all_nodes_ready_event(driver):
    """Test that the all nodes ready event is succesfully validated by pydantic."""
    event = Event("all nodes ready", {"source": "driver", "event": "all nodes ready"})
    driver.receive_event(event)


async def test_driver_ready_event(driver):
    """Test that the driver ready event is succesfully validated by pydantic."""
    event_type = "driver ready"
    event_data = {"source": "driver", "event": event_type}
    event = Event(event_type, event_data)

    def callback(data: dict) -> None:
        assert data == event_data

    driver.on(event_type, callback)
    driver.receive_event(event)


def test_config_manager(driver):
    """Test the driver has the config manager property."""
    assert driver.config_manager is not None
    assert driver.config_manager._client is driver.client


async def test_firmware_events(driver):
    """Test firmware events."""
    assert driver.firmware_update_progress is None
    event = Event(
        type="firmware update progress",
        data={
            "source": "driver",
            "event": "firmware update progress",
            "progress": {
                "sentFragments": 1,
                "totalFragments": 10,
                "progress": 10.0,
            },
        },
    )

    driver.receive_event(event)
    progress = event.data["firmware_update_progress"]
    assert progress.sent_fragments == 1
    assert progress.total_fragments == 10
    assert progress.progress == 10.0
    assert driver.firmware_update_progress
    assert driver.firmware_update_progress.sent_fragments == 1
    assert driver.firmware_update_progress.total_fragments == 10
    assert driver.firmware_update_progress.progress == 10.0

    event = Event(
        type="firmware update finished",
        data={
            "source": "driver",
            "event": "firmware update finished",
            "result": {"status": 255, "success": True},
        },
    )

    driver.receive_event(event)
    result = event.data["firmware_update_finished"]
    assert result.status == DriverFirmwareUpdateStatus.OK
    assert result.success
    assert driver.firmware_update_progress is None
