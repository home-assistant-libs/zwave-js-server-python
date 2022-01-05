"""Run a mock zwave-js-server instance off of a network state dump."""
import argparse
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from aiohttp import (
    WSMsgType,
    web,
    web_request,
)

from zwave_js_server.client import SIZE_PARSE_JSON_EXECUTOR
from zwave_js_server.const import (
    MAX_SERVER_SCHEMA_VERSION,
    MIN_SERVER_SCHEMA_VERSION,
    LogLevel,
)
from zwave_js_server.model.version import VersionInfoDataType

_LOGGER = logging.getLogger(__name__)


class ExitException(Exception):
    """Represent an exit error."""


class MockZwaveJsServer:
    """
    Class to represent a mock zwave-js-server instance.

    Only designed to handle one client at a time.
    """

    def __init__(self, network_state_dump: List[Dict[str, Any]]) -> None:
        """Initialize class."""
        self.network_state_dump = network_state_dump
        self.app = web.Application()
        self.app.add_routes([web.get("/", self.websocket_handler)])
        self.ws_resp: web.WebSocketResponse = None

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Send JSON."""
        _LOGGER.debug("Sending JSON: %s", data)
        await self.ws_resp.send_json(data)

    async def send_command_response(
        self,
        data: Dict[str, Any],
        message_id: str,
    ) -> None:
        """Send message."""
        await self.send_json({**data, "messageId": message_id})

    async def send_success_command_response(
        self,
        result: Optional[Dict[str, Any]],
        message_id: str,
    ) -> None:
        """Send success message."""
        if not result:
            result = {}
        await self.send_command_response(
            {"result": result, "type": "result", "success": True}, message_id
        )

    async def websocket_handler(
        self, request: web_request.Request
    ) -> web.WebSocketResponse:
        """Handle websocket requests."""
        self.ws_resp = web.WebSocketResponse(autoclose=False)
        await self.ws_resp.prepare(request)

        version_info: VersionInfoDataType = self.network_state_dump[0]
        # adjust min/max schemas if needed to get things to work
        if MAX_SERVER_SCHEMA_VERSION > version_info["maxSchemaVersion"]:
            version_info["maxSchemaVersion"] = MAX_SERVER_SCHEMA_VERSION
        if MIN_SERVER_SCHEMA_VERSION < version_info["minSchemaVersion"]:
            version_info["minSchemaVersion"] = MIN_SERVER_SCHEMA_VERSION
        await self.send_json(version_info)

        async for msg in self.ws_resp:
            if msg.type == WSMsgType.TEXT:
                try:
                    _LOGGER.debug("Message received: %s", msg.data)
                except TypeError:
                    _LOGGER.debug("Message received: %s", msg.data)
                if msg.data == "close":
                    await self.ws_resp.close()
                elif msg.data == "error":
                    _LOGGER.warning("Error from client: %s", msg.data)

                try:
                    if len(msg.data) > SIZE_PARSE_JSON_EXECUTOR:
                        data: dict = await asyncio.get_event_loop().run_in_executor(
                            None, msg.json
                        )
                    else:
                        data = msg.json()
                except ValueError as err:
                    raise ExitException(f"Received invalid JSON {msg.data}") from err

                if "command" not in data:
                    raise ExitException(f"Malformed message: {data}")

                cmd = data["command"]
                message_id = data["messageId"]
                if cmd == "set_api_schema":
                    await self.send_json(self.network_state_dump[1])
                elif cmd == "driver.get_log_config":
                    await self.send_success_command_response(
                        {
                            "config": {
                                "enabled": True,
                                "level": "silly",
                                "logToFile": False,
                                "nodeFilter": [],
                                "filename": None,
                                "forceConsole": False,
                            }
                        },
                        message_id,
                    )
                elif cmd == "start_listening":
                    await self.send_json(self.network_state_dump[2])
                else:
                    raise ExitException(f"Unknown data received: {data}")
            elif msg.type == WSMsgType.ERROR:
                _LOGGER.error(
                    "ws connection closed with exception %s", self.ws_resp.exception()
                )

        _LOGGER.info("websocket connection closed")

        return self.ws_resp


def main() -> None:
    """Run main entrypoint."""
    parser = argparse.ArgumentParser(description="Dump Instance")
    parser.add_argument(
        "network_state_path", type=str, help="File path to network state dump JSON."
    )
    parser.add_argument("--host", type=str, help="Host to bind to", default="127.0.0.1")
    parser.add_argument(
        "--port", type=int, help="Port to run on (defaults to 3000)", default=3000
    )
    parser.add_argument(
        "--loglevel",
        type=str.upper,
        help="Log level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args()

    # TODO: set logging level properly
    _LOGGER.setLevel(args.loglevel.upper())

    with open(args.network_state_path, "r", encoding="utf8") as fp:
        network_state_dump: List[Dict[str, Any]] = json.load(fp)

    server = MockZwaveJsServer(network_state_dump)
    web.run_app(server.app, host=args.host, port=args.port)


if __name__ == "__main__":
    try:
        main()
    except ExitException as error:
        _LOGGER.error("Fatal error: %s", error)
