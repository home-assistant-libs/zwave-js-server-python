"""Represents the version from the server."""

from dataclasses import dataclass


@dataclass
class VersionInfo:
    """Version info of the server."""

    driver_version: str
    server_version: str
    home_id: int
    min_scheme_version: int
    max_scheme_version: int

    @classmethod
    def from_message(cls, msg: dict) -> "VersionInfo":
        """Create a version info from a version message."""
        return cls(
            driver_version=msg["driverVersion"],
            server_version=msg["serverVersion"],
            home_id=msg["homeId"],
            min_scheme_version=msg.get("minSchemeVersion", 0),
            max_scheme_version=msg.get("maxSchemeVersion", 0)
        )
