"""Basic CLI to test Z-Wave JS server."""
import asyncio
import logging
import sys

import aiohttp

from .client import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__package__)


async def main():
    """Run main."""
    if len(sys.argv) < 2:
        print("Error: pass URL to Z-Wave JS server")
        return

    async with aiohttp.ClientSession() as session:
        client = Client(sys.argv[1], session)
        asyncio.create_task(client.connect())

        setup = False

        def log_value_updated(event):
            node = event["node"]
            value = event["value"]

            if node.device_config:
                description = node.device_config["description"]
            else:
                description = f'{node.device_class["generic"]} (missing device config)'

            logger.info(
                "Node %s %s (%s) changed to %s",
                description,
                value.property_name or "",
                value.value_id,
                value.value,
            )

        while True:
            try:
                await asyncio.sleep(0.1)

                if not setup and client.driver:
                    setup = True

                    # Set up listeners on new nodes
                    client.driver.controller.on(
                        "node added",
                        lambda event: event["node"].on(
                            "value updated", log_value_updated
                        ),
                    )

                    # Set up listeners on existing nodes
                    for node in client.driver.controller.nodes.values():
                        node.on("value updated", log_value_updated)
            except KeyboardInterrupt:
                logger.info("Close requested")
                break

        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
