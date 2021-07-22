"""Support for multicast commands."""
from typing import Any, List, Optional, cast

from zwave_js_server.model.node import Node

from ..client import Client
from ..const import CommandClass
from ..exceptions import NotFoundError
from ..model.value import ValueDataType, _get_value_id_from_dict


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
    value_data: ValueDataType,
    nodes: Optional[List[Node]] = None,
    options: Optional[dict] = None,
) -> bool:
    """Send a multicast set_value command."""
    assert client.driver
    # Iterate through nodes specified or all nodes if not specified
    for node in nodes or client.driver.controller.nodes.values():
        value_id = _get_value_id_from_dict(node, value_data)
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
        valueId=value_data,
        value=new_value,
        options=options,
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


async def async_multicast_endpoint_invoke_cc_api(
    client: Client,
    endpoint: int,
    command_class: CommandClass,
    method_name: str,
    args: Optional[List[Any]] = None,
    nodes: Optional[List[Node]] = None,
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
    nodes: Optional[List[Node]] = None,
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
