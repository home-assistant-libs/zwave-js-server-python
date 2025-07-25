"""
Model for Z-Wave JS config manager.

https://zwave-js.github.io/node-zwave-js/#/api/config-manager
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..device_config import DeviceConfig

if TYPE_CHECKING:
    from ...client import Client


class ConfigManager:
    """Model for the Z-Wave JS config manager."""

    def __init__(self, client: Client) -> None:
        """Initialize."""
        self._client = client

    async def lookup_device(
        self,
        manufacturer_id: int,
        product_type: int,
        product_id: int,
        firmware_version: str | None = None,
    ) -> DeviceConfig | None:
        """Look up the definition of a given device in the configuration DB."""
        cmd: dict[str, Any] = {
            "command": "config_manager.lookup_device",
            "manufacturerId": manufacturer_id,
            "productType": product_type,
            "productId": product_id,
        }

        if firmware_version is not None:
            cmd["firmwareVersion"] = firmware_version

        data = await self._client.async_send_command(cmd)

        if not data or not (config := data.get("config")):
            return None

        return DeviceConfig(config)
