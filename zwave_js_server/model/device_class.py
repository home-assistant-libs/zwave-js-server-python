"""
Model for a Zwave Node's device class.

https://zwave-js.github.io/node-zwave-js/#/api/node?id=deviceclass
"""

from typing import List, Optional


class DeviceClass:
    """Model for a Zwave Node's device class."""

    def __init__(self, data: dict) -> None:
        """Initialize."""
        self.data = data

    @property
    def basic(self) -> Optional[str]:
        """Return basic property."""
        return self.data.get("basic")

    @property
    def generic(self) -> Optional[str]:
        """Return generic property."""
        return self.data.get("generic")

    @property
    def specific(self) -> Optional[str]:
        """Return specific property."""
        return self.data.get("specific")

    @property
    def mandatory_supported_ccs(self) -> List[str]:
        """Return mandatorySupportedCCs property."""
        return self.data.get("mandatorySupportedCCs", [])

    @property
    def mandatory_controlled_ccs(self) -> List[str]:
        """Return mandatoryControlledCCs property."""
        # TODO: either there's a typo in the docs or the implementation
        return self.data.get("mandatoryControlCCs", [])
