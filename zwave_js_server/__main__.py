"""Basic CLI to test Z-Wave JS server."""
import argparse
import asyncio
import logging
import sys

import aiohttp

from .client import Client
from .dump import dump_msgs
from .version import get_server_version

logger = logging.getLogger(__package__)


def get_arguments() -> argparse.Namespace:
    """Get parsed passed in arguments."""

    parser = argparse.ArgumentParser(description="Z-Wave JS Server Python")
    parser.add_argument("--debug", action="store_true", help="Log with debug level")
    parser.add_argument(
        "--server-version", action="store_true", help="Print the version of the server"
    )
    parser.add_argument(
        "--dump-state", action="store_true", help="Dump the driver state"
    )
    parser.add_argument(
        "--event-timeout",
        help="How long to listen for events when dumping state",
    )
    parser.add_argument(
        "url",
        type=str,
        help="URL of server, ie ws://localhost:3000",
    )

    arguments = parser.parse_args()

    return arguments


async def start_cli() -> None:
    """Run main."""
    args = get_arguments()
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level)

    async with aiohttp.ClientSession() as session:
        if args.server_version:
            await print_version(args, session)
        elif args.dump_state:
            await handle_dump_state(args, session)
        else:
            await connect(args, session)


async def print_version(
    args: argparse.Namespace, session: aiohttp.ClientSession
) -> None:
    """Print the version of the server."""
    logger.setLevel(logging.WARNING)
    version = await get_server_version(args.url, session)
    print("Driver:", version.driver_version)
    print("Server:", version.server_version)
    print("Home ID:", version.home_id)


async def handle_dump_state(
    args: argparse.Namespace, session: aiohttp.ClientSession
) -> None:
    """Dump the state of the server."""
    timeout = None if args.event_timeout is None else float(args.event_timeout)
    msgs = await dump_msgs(args.url, session, timeout=timeout)
    for msg in msgs:
        print(msg)


async def connect(args: argparse.Namespace, session: aiohttp.ClientSession) -> None:
    """Connect to the server."""
    async with Client(args.url, session) as client:

        driver_ready = asyncio.Event()
        asyncio.create_task(on_driver_ready(client, driver_ready))

        await client.listen(driver_ready)


async def on_driver_ready(client: Client, driver_ready: asyncio.Event) -> None:
    """Act on driver ready."""
    await driver_ready.wait()

    assert client.driver
    # Set up listeners on new nodes
    client.driver.controller.on(
        "node added",
        lambda event: event["node"].on("value updated", log_value_updated),
    )

    # Set up listeners on existing nodes
    for node in client.driver.controller.nodes.values():
        node.on("value updated", log_value_updated)


def log_value_updated(event: dict) -> None:
    """Log node value changes."""
    node = event["node"]
    value = event["value"]

    if node.device_config:
        description = node.device_config.description
    else:
        description = f"{node.device_class.generic} (missing device config)"

    logger.info(
        "Node %s %s (%s) changed to %s",
        description,
        value.property_name or "",
        value.value_id,
        value.value,
    )


def main() -> None:
    """Run main."""
    try:
        asyncio.run(start_cli())
    except KeyboardInterrupt:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
