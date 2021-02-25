"""Represents the version from the server."""

from dataclasses import dataclass


@dataclass
class VersionInfo:
    """Version info of the server."""

    driver_version: str
    server_version: str
    home_id: int
    min_schema_version: int
    max_schema_version: int

    @classmethod
    def from_message(cls, msg: dict) -> "VersionInfo":
        """Create a version info from a version message."""
        return cls(
            driver_version=msg["driverVersion"],
            server_version=msg["serverVersion"],
            home_id=msg["homeId"],
            # schema versions are sent in the response from schema version 1+
            # this info not present means the server is at schema version 0
            # at some point in time (when we stop supporting schema version 0),
            # we could adjust this code and assume the keys are there.
            min_schema_version=msg.get("minSchemaVersion", 0),
            max_schema_version=msg.get("maxSchemaVersion", 0),
        )
