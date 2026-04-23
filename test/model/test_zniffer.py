"""Test the zniffer model."""

from zwave_js_server.client import Client
from zwave_js_server.model.zniffer import Zniffer

from ..common import MockCommandProtocol


async def test_zniffer_lifecycle(
    client: Client, mock_command: MockCommandProtocol
) -> None:
    """Test zniffer init, start, stop, destroy lifecycle."""
    zniffer = Zniffer(client)

    mock_command({"command": "zniffer.init"}, {})
    mock_command({"command": "zniffer.start"}, {})
    mock_command({"command": "zniffer.stop"}, {})
    mock_command({"command": "zniffer.destroy"}, {})

    await zniffer.async_init("/dev/ttyACM0", options={"logConfig": {}})
    await zniffer.async_start()
    await zniffer.async_stop()
    await zniffer.async_destroy()


async def test_zniffer_capture_operations(
    client: Client, mock_command: MockCommandProtocol
) -> None:
    """Test capture-related zniffer commands."""
    zniffer = Zniffer(client)

    mock_command({"command": "zniffer.clear_captured_frames"}, {})
    await zniffer.async_clear_captured_frames()

    mock_command(
        {"command": "zniffer.get_capture_as_zlf_buffer"}, {"capture": "AQIDBA=="}
    )
    assert await zniffer.async_get_capture_as_zlf_buffer() == b"\x01\x02\x03\x04"

    mock_command(
        {"command": "zniffer.captured_frames"},
        {"capturedFrames": [{"type": "data"}]},
    )
    assert await zniffer.async_captured_frames() == [{"type": "data"}]


async def test_zniffer_frequency_operations(
    client: Client, mock_command: MockCommandProtocol
) -> None:
    """Test frequency-related zniffer commands."""
    zniffer = Zniffer(client)

    mock_command(
        {"command": "zniffer.supported_frequencies"},
        {"frequencies": {"0": "EU", "1": "US"}},
    )
    assert await zniffer.async_supported_frequencies() == {0: "EU", 1: "US"}

    mock_command({"command": "zniffer.current_frequency"}, {"frequency": 0})
    assert await zniffer.async_current_frequency() == 0

    ack_commands = mock_command({"command": "zniffer.set_frequency"}, {})
    await zniffer.async_set_frequency(1)
    assert ack_commands[-1]["frequency"] == 1


async def test_zniffer_current_frequency_none(
    client: Client, mock_command: MockCommandProtocol
) -> None:
    """Test current frequency returns None when not set."""
    zniffer = Zniffer(client)
    mock_command({"command": "zniffer.current_frequency"}, {})
    assert await zniffer.async_current_frequency() is None


async def test_zniffer_lr_commands(
    client: Client, mock_command: MockCommandProtocol
) -> None:
    """Test Long Range zniffer commands (schema 47+)."""
    zniffer = Zniffer(client)

    mock_command({"command": "zniffer.get_lr_regions"}, {"regions": [1, 2]})
    assert await zniffer.async_get_lr_regions() == [1, 2]

    mock_command(
        {"command": "zniffer.get_current_lr_channel_config"}, {"channelConfig": 3}
    )
    assert await zniffer.async_get_current_lr_channel_config() == 3

    mock_command(
        {"command": "zniffer.get_supported_lr_channel_configs"},
        {"channelConfigs": {"0": "Config A", "1": "Config B"}},
    )
    assert await zniffer.async_get_supported_lr_channel_configs() == {
        0: "Config A",
        1: "Config B",
    }

    ack_commands = mock_command({"command": "zniffer.set_lr_channel_config"}, {})
    await zniffer.async_set_lr_channel_config(1)
    assert ack_commands[-1]["channelConfig"] == 1


async def test_zniffer_lr_channel_config_none(
    client: Client, mock_command: MockCommandProtocol
) -> None:
    """Test LR channel config returns None when not set."""
    zniffer = Zniffer(client)
    mock_command({"command": "zniffer.get_current_lr_channel_config"}, {})
    assert await zniffer.async_get_current_lr_channel_config() is None


async def test_zniffer_load_capture_from_buffer(
    client: Client, mock_command: MockCommandProtocol
) -> None:
    """Test load capture from buffer command (schema 47+)."""
    zniffer = Zniffer(client)
    ack_commands = mock_command({"command": "zniffer.load_capture_from_buffer"}, {})
    await zniffer.async_load_capture_from_buffer(b"\x01\x02\x03")
    assert ack_commands[0]["data"] == "AQID"
