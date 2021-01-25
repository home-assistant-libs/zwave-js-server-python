"""Version helper."""
from typing import cast

import aiohttp

from .client import Client, VersionInfo


async def get_server_version(url: str, session: aiohttp.ClientSession) -> VersionInfo:
    """Return a server version."""
    client = Client(url, session, start_listening_on_connect=False)

    async def handle_connected() -> None:
        await client.disconnect()

    client.register_on_connect(handle_connected)

    await client.connect()
    return cast(VersionInfo, client.version)
