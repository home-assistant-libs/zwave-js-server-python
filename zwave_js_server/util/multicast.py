"""Support for multicast commands."""

from typing import Any, List, Optional, Union, cast
from zwave_js_server.model.node import Node

from ..client import Client
from ..const import CommandClass
from ..model.value import Value, ValueDataType


async def _async_send_command(
    client: Client,
    command: str,
    nodes: Optional[List[Node]] = None,
    require_schema: Optional[int] = None,
    **kwargs: Any,
) -> dict:
    """Send a multicast command."""
    if nodes:
        cmd = {
            "command": f"multicast_group.{command}",
            "nodeIDs": [node.node_id for node in nodes],
            **kwargs,
        }
    else:
        cmd = {"command": f"broadcast_node.{command}", **kwargs}

    return await client.async_send_command(cmd, require_schema)


async def async_multicast_set_value(
    client: Client,
    new_value: Any,
    val: Union[Value, ValueDataType],
    nodes: Optional[List[Node]] = None,
) -> bool:
    """Send a multicast set_value command."""
    value_id = val.data if isinstance(val, Value) else val

    result = await _async_send_command(
        client,
        "set_value",
        nodes,
        valueId=value_id,
        value=new_value,
        require_schema=5,
    )
    return cast(bool, result["success"])


async def async_multicast_get_endpoint_count(
    client: Client, nodes: Optional[List[Node]] = None
) -> int:
    """Send a multicast get_endpoint_count command."""
    result = await _async_send_command(
        client, "get_endpoint_count", nodes, require_schema=5
    )
    return cast(int, result["count"])


async def async_multicast_endpoint_supports_cc(
    client: Client,
    endpoint: int,
    command_class: CommandClass,
    nodes: Optional[List[Node]] = None,
) -> bool:
    """Send a supports_cc command to a multicast endpoint."""
    result = await _async_send_command(
        client,
        "supports_cc",
        nodes,
        index=endpoint,
        commandClass=command_class,
        require_schema=5,
    )
    return cast(bool, result["supported"])


async def async_multicast_endpoint_get_cc_version(
    client: Client,
    endpoint: int,
    command_class: CommandClass,
    nodes: Optional[List[Node]] = None,
) -> int:
    """Send a get_cc_version command to a multicast endpoint."""
    result = await _async_send_command(
        client,
        "get_cc_version",
        nodes,
        index=endpoint,
        commandClass=command_class,
        require_schema=5,
    )
    return cast(int, result["version"])
