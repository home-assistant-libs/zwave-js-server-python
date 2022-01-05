"""Run a mock zwave-js-server instance off of a network state dump."""
import argparse
import asyncio
import json
from typing import Any, Dict, List, Optional

from aiohttp import (
    WSMsgType,
    web,
    web_request,
)

from zwave_js_server.client import SIZE_PARSE_JSON_EXECUTOR
from zwave_js_server.const import MAX_SERVER_SCHEMA_VERSION, MIN_SERVER_SCHEMA_VERSION
from zwave_js_server.model.version import VersionInfoDataType


class ExitException(Exception):
    """Represent an exit error."""


def get_args() -> argparse.Namespace:
    """Get arguments."""
    parser = argparse.ArgumentParser(description="Dump Instance")
    parser.add_argument(
        "network_state_path", type=str, help="File path to network state dump JSON."
    )
    parser.add_argument("--host", type=str, help="Host to bind to", default="127.0.0.1")
    parser.add_argument(
        "--port", type=int, help="Port to run on (defaults to 3000)", default=3000
    )
    return parser.parse_args()


async def send_json(ws_resp: web.WebSocketResponse, data: Dict[str, Any]) -> None:
    """Send JSON."""
    print(f"Sending JSON: {data}")
    await ws_resp.send_json(data)


async def send_msg(
    ws_resp: web.WebSocketResponse,
    request: Dict[str, Any],
    data: Dict[str, Any],
) -> None:
    """Send message."""
    await send_json(ws_resp, {**data, "messageId": request["messageId"]})


async def send_success_msg(
    ws_resp: web.WebSocketResponse,
    request: Dict[str, Any],
    data: Optional[Dict[str, Any]],
) -> None:
    """Send success message."""
    if not data:
        data = {}
    await send_msg(
        ws_resp, request, {"result": data, "type": "result", "success": True}
    )


def main():
    """Run main entrypoint."""
    args = get_args()
    with open(args.network_state_path, "r", encoding="utf8") as fp:
        network_state_dump: List[Dict[str, Any]] = json.load(fp)

    vars = {"first_request": True}

    async def websocket_handler(request: web_request.Request):
        """Handle websocket requests."""
        ws_resp = web.WebSocketResponse(autoclose=False)
        await ws_resp.prepare(request)

        if vars["a"]:
            vars["a"] = False
            version_info: VersionInfoDataType = network_state_dump.pop(0)
            # adjust min/max schemas if needed to get things to work
            if MAX_SERVER_SCHEMA_VERSION > version_info["maxSchemaVersion"]:
                version_info["maxSchemaVersion"] = MAX_SERVER_SCHEMA_VERSION
            if MIN_SERVER_SCHEMA_VERSION < version_info["minSchemaVersion"]:
                version_info["minSchemaVersion"] = MIN_SERVER_SCHEMA_VERSION
            await send_json(ws_resp, version_info)

        async for msg in ws_resp:
            if msg.type == WSMsgType.TEXT:
                print(f"Message received: {msg.data}")
                if msg.data == "close":
                    await ws_resp.close()
                elif msg.data == "error":
                    print(f"Error from client: {msg}")

                try:
                    if len(msg.data) > SIZE_PARSE_JSON_EXECUTOR:
                        data: dict = await asyncio.get_event_loop().run_in_executor(
                            None, msg.json
                        )
                    else:
                        data = msg.json()
                except ValueError as err:
                    raise ExitException("Received invalid JSON.") from err

                if "command" not in data:
                    raise ExitException(f"Malformed message: {data}")
                cmd = data["command"]
                if cmd == "set_api_schema":
                    await send_json(ws_resp, network_state_dump.pop(0))
                elif cmd == "driver.get_log_config":
                    await send_success_msg(
                        ws_resp,
                        data,
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
                    )
                elif cmd == "start_listening":
                    await send_json(ws_resp, network_state_dump.pop(0))
                else:
                    raise ExitException(f"Unknown data received: {data}")
            elif msg.type == WSMsgType.ERROR:
                print(f"ws connection closed with exception {ws_resp.exception()}")

        print("websocket connection closed")

        return ws_resp

    app = web.Application()
    app.add_routes([web.get("/", websocket_handler)])
    web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    try:
        main()
    except ExitException as error:
        print(f"Fatal error: {error}")
