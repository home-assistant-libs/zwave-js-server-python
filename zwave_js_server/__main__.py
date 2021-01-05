"""Basic CLI to test wrapper."""
import asyncio
import aiohttp
import logging
import sys

from .client import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__package__)


async def main():
    if len(sys.argv) < 2:
        print("Error: pass URL to Z-Wave JS server")
        return

    async with aiohttp.ClientSession() as session:
        client = Client(sys.argv[1], session)
        asyncio.create_task(client.connect())

        while True:
            try:
                await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                logger.info("Close requested")
                break

        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
