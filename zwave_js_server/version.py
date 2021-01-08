"""Version helper."""
from dataclasses import dataclass

import aiohttp


@dataclass
class VersionInfo:
    """Version info of the server."""

    driver_version: str
    server_version: str
    home_id: int

    @classmethod
    def from_message(cls, msg: dict) -> "VersionInfo":
        """Create a version info from a version message."""
        return cls(
            driver_version=msg["driverVersion"],
            server_version=msg["serverVersion"],
            home_id=msg["homeId"],
        )


async def get_server_version(url: str, session: aiohttp.ClientSession) -> VersionInfo:
    """Return a server version."""
    client = await session.ws_connect(
        url,
    )
    try:
        return VersionInfo.from_message(await client.receive_json())
    finally:
        await client.close()
