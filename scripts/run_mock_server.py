"""Run a mock zwave-js-server instance off of a network state dump."""
import argparse
import asyncio
from collections import defaultdict
from collections.abc import Hashable
from functools import wraps
import json
import logging
from typing import Callable, DefaultDict, List, Optional, Union

from aiohttp import WSMsgType, web, web_request

from zwave_js_server.client import SIZE_PARSE_JSON_EXECUTOR
from zwave_js_server.const import MAX_SERVER_SCHEMA_VERSION, MIN_SERVER_SCHEMA_VERSION
from zwave_js_server.model.version import VersionInfoDataType

DATEFMT = "%Y-%m-%d %H:%M:%S"
FMT = "%(asctime)s [%(levelname)s] %(message)s"


class ExitException(Exception):
    """Represent an exit error."""


# https://stackoverflow.com/a/1151686
class HashableDict(dict):
    """Dictionary that can be used as a key in a dictionary."""

    def __key(self) -> tuple:
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other) -> bool:
        # pylint: disable=protected-access
        return self.__key() == other.__key()


class MockZwaveJsServer:
    """
    Class to represent a mock zwave-js-server instance.

    Only designed to handle one client at a time.
    """

    def __init__(
        self,
        network_state_dump: List[dict],
        events_to_replay: List[dict],
        command_responses: DefaultDict[HashableDict, list],
    ) -> None:
        """Initialize class."""
        self.network_state_dump = network_state_dump
        self.app = web.Application()
        self.app.add_routes(
            [
                web.get("/", self.server_handler),
                web.post("/replay", self.replay_handler),
            ]
        )
        self.primary_ws_resp: Optional[web.WebSocketResponse] = None
        self.events_to_replay = events_to_replay
        self.command_responses = command_responses

    async def send_json(self, data: dict) -> None:
        """Send JSON."""
        logging.debug("Sending JSON: %s", data)
        assert self.primary_ws_resp is not None
        await self.primary_ws_resp.send_json(data)

    async def send_command_response(
        self,
        data: dict,
        message_id: str,
    ) -> None:
        """Send message."""
        await self.send_json({**data, "messageId": message_id})

    async def send_success_command_response(
        self,
        result: Optional[dict],
        message_id: str,
    ) -> None:
        """Send success message."""
        if result is None:
            result = {}
        await self.send_command_response(
            {"result": result, "type": "result", "success": True}, message_id
        )

    async def process_record(self, record: dict) -> None:
        """Process a replay dump record."""
        if record["record_type"] == "event":
            await self.send_json(record)
        elif record["record_type"] == "command":
            add_command_response(self.command_responses, record)
        else:
            raise ExitException(f"Malformed record: {record}")

    async def server_handler(self, request: web_request.Request) -> web.WebSocketResponse:
        """Handle websocket requests to the server."""
        ws_resp = web.WebSocketResponse(autoclose=False)
        self.primary_ws_resp = ws_resp
        await ws_resp.prepare(request)

        version_info: VersionInfoDataType = self.network_state_dump[0]
        # adjust min/max schemas if needed to get things to work
        if MAX_SERVER_SCHEMA_VERSION > version_info["maxSchemaVersion"]:
            version_info["maxSchemaVersion"] = MAX_SERVER_SCHEMA_VERSION
        if MIN_SERVER_SCHEMA_VERSION < version_info["minSchemaVersion"]:
            version_info["minSchemaVersion"] = MIN_SERVER_SCHEMA_VERSION
        await self.send_json(version_info)

        async for msg in ws_resp:
            if msg.type == WSMsgType.TEXT:
                logging.debug("Message received: %s", msg.data)
                if msg.data == "close":
                    await ws_resp.close()
                elif msg.data == "error":
                    logging.warning("Error from client: %s", msg.data)

                try:
                    if len(msg.data) > SIZE_PARSE_JSON_EXECUTOR:
                        data: Union[
                            dict, list
                        ] = await asyncio.get_event_loop().run_in_executor(
                            None, msg.json
                        )
                    else:
                        data = msg.json()
                except ValueError as err:
                    raise ExitException(
                        f"Received invalid JSON {msg.data}"
                    ) from err

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
                    await asyncio.sleep(1)
                    for event in self.events_to_replay:
                        await self.send_json(event)
                elif resp_list := self.command_responses[sanitize_msg(data)]:
                    await self.send_command_response(resp_list.pop(0), message_id)
                else:
                    raise ExitException(f"Unhandled command received: {data}")
            elif msg.type == WSMsgType.ERROR:
                logging.error(
                    "Connection closed with exception %s",
                    ws_resp.exception(),
                )

        logging.info("Connection closed")

        return ws_resp

    async def replay_handler(self, request: web_request.Request) -> web.Response:
        """Handle requests to replay dump."""
        try:
            data = await request.json()
        except json.decoder.JSONDecodeError:
            return web.Response(status=400, reason="Invalid JSON.")

        if isinstance(data, list):
            for record in data:
                self.process_record(record)
        elif isinstance(data, dict):
            self.process_record(data)
        else:
            return web.Response(status=400, reason=f"Malformed message: {data}")
        return web.Response(status=200)


def _hashable_value(item: Union[dict, list, Hashable]) -> Union[tuple, list, Hashable]:
    """Return hashable value from item."""
    if isinstance(item, dict):
        return make_dict_hashable(item)
    if isinstance(item, list):
        return make_list_hashable(item)
    return item


def make_list_hashable(lst: list) -> tuple:
    """Make a list hashable."""
    return tuple(_hashable_value(item) for item in lst)


def make_dict_hashable(dct: dict) -> HashableDict:
    """Convert a dictionary to a hashable dictionary."""
    return HashableDict({key: _hashable_value(value) for key, value in dct.items()})


def sanitize_msg(msg: dict) -> HashableDict:
    """Sanitize command message."""
    msg = msg.copy()
    msg.pop("messageId", None)
    return make_dict_hashable(msg)


def add_command_response(
    command_responses: DefaultDict[HashableDict, list],
    record: dict,
) -> None:
    """Add a command response to command_responses map."""
    command_msg = sanitize_msg(record["command_msg"])
    # Response message doesn't need to be sanitized here because it will be sanitized
    # in the MockZwaveJsServer.send_command_response method.
    response_msg = record["response_msg"]
    command_responses[command_msg].append(response_msg)


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
    parser.add_argument(
        "--log-level",
        type=str.upper,
        help="Log level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    parser.add_argument(
        "--events-to-replay-path",
        type=str,
        help=(
            "File path to events to replay JSON. Events provided by --combined-replay-dump-path"
            "option will be first, followed by events from this file."
        ),
        default=None,
    )
    parser.add_argument(
        "--command-responses-path",
        type=str,
        help=(
            "File path to command response JSON. Command responses provided by "
            "--combined-replay-dump-path option will be first, followed by responses from this"
            "file."
        ),
        default=None,
    )
    parser.add_argument(
        "--combined-replay-dump-path",
        type=str,
        help=(
            "File path to the combined event and command response dump JSON. Events and "
            "command responses will be extracted in the order they were received."
        ),
        default=None,
    )
    return parser.parse_args()


def main() -> None:
    """Run main entrypoint."""
    args = get_args()

    with open(args.network_state_path, "r", encoding="utf8") as fp:
        network_state_dump: List[dict] = json.load(fp)

    events_to_replay = []
    command_responses: DefaultDict[HashableDict, list] = defaultdict(list)

    if args.combined_replay_dump_path:
        with open(args.combined_replay_dump_path, "r", encoding="utf8") as fp:
            records: List[dict] = json.load(fp)

            for record in records:
                if record["record_type"] == "event":
                    events_to_replay.append(record["data"])
                elif record["record_type"] == "command":
                    add_command_response(command_responses, record)

    if args.events_to_replay_path:
        with open(args.events_to_replay_path, "r", encoding="utf8") as fp:
            records = json.load(fp)
            if any(record["record_type"] != "event" for record in records):
                raise ExitException("Invalid record type in event replay dump file")
            for record in records:
                events_to_replay.append(record["data"])

    if args.command_responses_path:
        with open(args.command_responses_path, "r", encoding="utf8") as fp:
            records = json.load(fp)
            if any(record["record_type"] != "command" for record in records):
                raise ExitException(
                    "Invalid record type in command responses dump file"
                )
            for record in records:
                add_command_response(command_responses, record)

    # adapted from homeassistant.bootstrap.async_enable_logging
    logging.basicConfig(level=args.log_level)
    try:
        # pylint: disable=import-outside-toplevel
        from colorlog import ColoredFormatter

        colorfmt = f"%(log_color)s{FMT}%(reset)s"
        logging.getLogger().handlers[0].setFormatter(
            ColoredFormatter(
                colorfmt,
                datefmt=DATEFMT,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red",
                },
            )
        )
    except ImportError:
        logging.getLogger().handlers[0].setFormatter(
            logging.Formatter(fmt=FMT, datefmt=DATEFMT)
        )

    server = MockZwaveJsServer(network_state_dump, events_to_replay, command_responses)
    web.run_app(server.app, host=args.host, port=args.port)


if __name__ == "__main__":
    try:
        main()
    except ExitException as error:
        logging.error("Fatal error: %s", error)
