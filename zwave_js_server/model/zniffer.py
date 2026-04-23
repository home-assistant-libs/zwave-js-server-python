"""Provide a model for the Z-Wave JS Zniffer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..util.helpers import convert_base64_to_bytes, convert_bytes_to_base64

if TYPE_CHECKING:
    from ..client import Client


class Zniffer:
    """Represent a Z-Wave JS Zniffer."""

    def __init__(self, client: Client) -> None:
        """Initialize zniffer."""
        self.client = client

    async def _async_send_command(
        self, command: str, require_schema: int | None = None, **kwargs: Any
    ) -> dict:
        """Send a zniffer command. For internal use only."""
        return await self.client.async_send_command(
            {
                "command": f"zniffer.{command}",
                **kwargs,
            },
            require_schema,
        )

    async def async_init(self, device_path: str, options: dict | None = None) -> None:
        """Initialize the zniffer with a device path."""
        kwargs: dict[str, Any] = {"devicePath": device_path}
        if options is not None:
            kwargs["options"] = options
        await self._async_send_command("init", **kwargs)

    async def async_start(self) -> None:
        """Start capturing frames."""
        await self._async_send_command("start")

    async def async_stop(self) -> None:
        """Stop capturing frames."""
        await self._async_send_command("stop")

    async def async_destroy(self) -> None:
        """Destroy the zniffer instance."""
        await self._async_send_command("destroy")

    async def async_clear_captured_frames(self) -> None:
        """Clear all captured frames."""
        await self._async_send_command("clear_captured_frames")

    async def async_get_capture_as_zlf_buffer(self) -> bytes:
        """Get captured frames as a ZLF buffer."""
        data = await self._async_send_command("get_capture_as_zlf_buffer")
        return convert_base64_to_bytes(data["capture"])

    async def async_captured_frames(self) -> list[dict]:
        """Get list of captured frames."""
        data = await self._async_send_command("captured_frames")
        return list(data["capturedFrames"])

    async def async_supported_frequencies(self) -> dict[int, str]:
        """Get supported frequencies as a mapping of frequency ID to name."""
        data = await self._async_send_command("supported_frequencies")
        return {int(k): v for k, v in data["frequencies"].items()}

    async def async_current_frequency(self) -> int | None:
        """Get the current frequency."""
        data = await self._async_send_command("current_frequency")
        return data.get("frequency")

    async def async_set_frequency(self, frequency: int) -> None:
        """Set the capture frequency."""
        await self._async_send_command("set_frequency", frequency=frequency)

    async def async_get_lr_regions(self) -> list[int]:
        """Get the supported Long Range regions."""
        data = await self._async_send_command("get_lr_regions", require_schema=47)
        return list(data["regions"])

    async def async_get_current_lr_channel_config(self) -> int | None:
        """Get the current Long Range channel configuration."""
        data = await self._async_send_command(
            "get_current_lr_channel_config", require_schema=47
        )
        return data.get("channelConfig")

    async def async_get_supported_lr_channel_configs(self) -> dict[int, str]:
        """Get supported LR channel configs as a mapping of config ID to name."""
        data = await self._async_send_command(
            "get_supported_lr_channel_configs", require_schema=47
        )
        return {int(k): v for k, v in data["channelConfigs"].items()}

    async def async_set_lr_channel_config(self, channel_config: int) -> None:
        """Set the Long Range channel configuration."""
        await self._async_send_command(
            "set_lr_channel_config",
            require_schema=47,
            channelConfig=channel_config,
        )

    async def async_load_capture_from_buffer(self, data: bytes) -> None:
        """Load a capture from a binary buffer."""
        await self._async_send_command(
            "load_capture_from_buffer",
            require_schema=47,
            data=convert_bytes_to_base64(data),
        )
