"""Version helper."""
import aiohttp

from .model.version import VersionInfo


async def get_server_version(url: str, session: aiohttp.ClientSession) -> VersionInfo:
    """Return a server version."""
    client = await session.ws_connect(url)
    try:
        return VersionInfo.from_message(await client.receive_json())
    finally:
        await client.close()
