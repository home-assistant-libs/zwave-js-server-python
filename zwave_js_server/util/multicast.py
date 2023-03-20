"""Support for multicast commands."""
from __future__ import annotations

from typing import Any, cast

from ..client import Client
from ..const import TARGET_VALUE_PROPERTY, CommandClass
from ..exceptions import NotFoundError
from ..model.node import Node, _get_value_id_dict_from_value_data
from ..model.value import ValueDataType, _get_value_id_str_from_dict


async def _async_send_command(
    client: Client,
    command: str,
    nodes: list[Node] | None = None,
    require_schema: int | None = None,
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
    value_data: ValueDataType,
    nodes: list[Node] | None = None,
    options: dict | None = None,
) -> bool:
    """Send a multicast set_value command."""
    assert client.driver
    # Iterate through nodes specified (if any) and validate that the value exists
    for node in nodes or ():
        # If the value to set is for Basic CC and targetValue property, skip validation
        if (
            value_data["commandClass"] == CommandClass.BASIC
            and value_data["property"] == TARGET_VALUE_PROPERTY
        ):
            break
        value_id = _get_value_id_str_from_dict(node, value_data)
        # Check that the value exists on the node
        if value_id not in node.values:
            raise NotFoundError(f"Node {node} doesn't have value {value_id}")
        # Check that the option is valid for the value
        for option in options or {}:
            if option not in node.values[value_id].metadata.value_change_options:
                raise NotFoundError(
                    f"Node {node} value {value_id} doesn't support option {option}"
                )

    result = await _async_send_command(
        client,
        "set_value",
        nodes,
        valueId=_get_value_id_dict_from_value_data(value_data),
        value=new_value,
        options=options,
        require_schema=5,
    )
    return cast(bool, result["success"])


async def async_multicast_get_endpoint_count(
    client: Client, nodes: list[Node] | None = None
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
    nodes: list[Node] | None = None,
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
    nodes: list[Node] | None = None,
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


async def async_multicast_endpoint_invoke_cc_api(
    client: Client,
    endpoint: int,
    command_class: CommandClass,
    method_name: str,
    args: list[Any] | None = None,
    nodes: list[Node] | None = None,
) -> Any:
    """Send a invoke_cc_api command to a multicast endpoint."""
    result = await _async_send_command(
        client,
        "invoke_cc_api",
        nodes,
        index=endpoint,
        commandClass=command_class,
        methodName=method_name,
        args=args,
        require_schema=5,
    )
    return result["response"]


async def async_multicast_endpoint_supports_cc_api(
    client: Client,
    endpoint: int,
    command_class: CommandClass,
    nodes: list[Node] | None = None,
) -> bool:
    """Send a supports_cc_api command to a multicast endpoint."""
    result = await _async_send_command(
        client,
        "supports_cc_api",
        nodes,
        index=endpoint,
        commandClass=command_class,
        require_schema=5,
    )
    return cast(bool, result["supported"])
