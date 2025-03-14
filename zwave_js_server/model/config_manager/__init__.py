"""
Model for Z-Wave JS config manager.

https://zwave-js.github.io/node-zwave-js/#/api/config-manager
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ...client import Client

from ..device_config import DeviceConfig


class ConfigManager:
    """Model for the Z-Wave JS config manager."""

    def __init__(self, client: Client) -> None:
        """Initialize."""
        self.client = client

    async def lookup_device(
        self,
        manufacturer_id: int,
        product_type: int,
        product_id: int,
        firmware_version: Optional[str] = None,
    ) -> Optional[DeviceConfig]:
        """Look up the definition of a given device in the configuration DB."""
        cmd: dict[str, Any] = {
            "command": "config_manager.lookup_device",
            "manufacturerId": manufacturer_id,
            "productType": product_type,
            "productId": product_id,
        }

        if firmware_version is not None:
            cmd["firmwareVersion"] = firmware_version

        data = await self.client.async_send_command(cmd)

        if not data or not data.get("config"):
            return None

        return DeviceConfig(data["config"])
