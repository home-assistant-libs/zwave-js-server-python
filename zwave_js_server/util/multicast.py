"""Support for multicast commands."""

from typing import Any, List, Optional, Union, cast

from ..client import Client
from ..const import CommandClass
from ..model.value import Value, ValueDataType


async def _async_send_command(
    client: Client,
    command: str,
    node_ids: Optional[List[int]] = None,
    require_schema: Optional[int] = None,
    **kwargs: Any,
) -> dict:
    """Send a multicast command."""
    if node_ids:
        cmd = {"command": f"multicast_group.{command}", "node_ids": node_ids, **kwargs}
    else:
        cmd = {"command": f"broadcast_node.{command}", **kwargs}

    return await client.async_send_command(cmd, require_schema)


async def async_multicast_set_value(
    client: Client,
    new_value: Any,
    val: Union[Value, ValueDataType],
    node_ids: Optional[List[int]] = None,
) -> bool:
    """Send a multicast set_value command."""
    value_id = val.data if isinstance(val, Value) else val

    result = await _async_send_command(
        client,
        "set_value",
        node_ids,
        valueId=value_id,
        value=new_value,
        require_schema=5,
    )
    return cast(bool, result["success"])


async def async_multicast_get_endpoint_count(
    client: Client, node_ids: Optional[List[int]] = None
) -> int:
    """Send a multicast get_endpoint_count command."""
    result = await _async_send_command(
        client, "get_endpoint_count", node_ids, require_schema=5
    )
    return cast(int, result["count"])


async def async_multicast_endpoint_supports_cc(
    client: Client,
    endpoint: int,
    command_class: CommandClass,
    node_ids: Optional[List[int]] = None,
) -> bool:
    """Send a supports_cc command to a multicast endpoint."""
    result = await _async_send_command(
        client,
        "supports_cc",
        node_ids,
        index=endpoint,
        commandClass=command_class,
        require_schema=5,
    )
    return cast(bool, result["supported"])


async def async_multicast_endpoint_get_cc_version(
    client: Client,
    endpoint: int,
    command_class: CommandClass,
    node_ids: Optional[List[int]] = None,
) -> int:
    """Send a get_cc_version command to a multicast endpoint."""
    result = await _async_send_command(
        client,
        "get_cc_version",
        node_ids,
        index=endpoint,
        commandClass=command_class,
        require_schema=5,
    )
    return cast(int, result["version"])
