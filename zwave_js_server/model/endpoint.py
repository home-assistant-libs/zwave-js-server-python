"""
Model for a Zwave Node's endpoints.

https://zwave-js.github.io/node-zwave-js/#/api/endpoint?id=endpoint-properties
"""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Literal, TypedDict, cast

from ..const import NodeStatus
from ..event import EventBase
from ..exceptions import FailedCommand, NotFoundError
from .command_class import CommandClass, CommandClassInfo, CommandClassInfoDataType
from .device_class import DeviceClass, DeviceClassDataType
from .value import (
    CommandStatus,
    ConfigurationValue,
    ConfigurationValueFormat,
    SetConfigParameterResult,
    SupervisionResult,
    Value,
)

if TYPE_CHECKING:
    from ..client import Client
    from .node import Node
    from .node.data_model import NodeDataType


class EndpointDataType(TypedDict, total=False):
    """Represent an endpoint data dict type."""

    nodeId: int  # required
    index: int  # required
    deviceClass: DeviceClassDataType | None
    installerIcon: int
    userIcon: int
    endpointLabel: str
    commandClasses: list[CommandClassInfoDataType]  # required


class Endpoint(EventBase):
    """Model for a Zwave Node's endpoint."""

    def __init__(
        self,
        client: Client,
        node: Node,
        data: EndpointDataType,
        values: dict[str, ConfigurationValue | Value],
    ) -> None:
        """Initialize."""
        super().__init__()
        self.client = client
        self.node = node
        self.data: EndpointDataType = data
        self.values: dict[str, ConfigurationValue | Value] = {}
        self.update(data, values)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{type(self).__name__}(node_id={self.node_id}, index={self.index})"

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.client.driver, self.node_id, self.index))

    def __eq__(self, other: object) -> bool:
        """Return whether this instance equals another."""
        if not isinstance(other, Endpoint):
            return False
        return (
            self.client.driver == other.client.driver
            and self.node_id == other.node_id
            and self.index == other.index
        )

    @property
    def node_id(self) -> int:
        """Return node ID property."""
        return self.data["nodeId"]

    @property
    def index(self) -> int:
        """Return index property."""
        return self.data["index"]

    @property
    def device_class(self) -> DeviceClass | None:
        """Return the device_class."""
        if (device_class := self.data.get("deviceClass")) is None:
            return None
        return DeviceClass(device_class)

    @property
    def installer_icon(self) -> int | None:
        """Return installer icon property."""
        return self.data.get("installerIcon")

    @property
    def user_icon(self) -> int | None:
        """Return user icon property."""
        return self.data.get("userIcon")

    @property
    def command_classes(self) -> list[CommandClassInfo]:
        """Return all CommandClasses supported on this node."""
        return [CommandClassInfo(cc) for cc in self.data["commandClasses"]]

    @property
    def endpoint_label(self) -> str | None:
        """Return endpoint label property."""
        return self.data.get("endpointLabel")

    def update(
        self, data: EndpointDataType, values: dict[str, ConfigurationValue | Value]
    ) -> None:
        """Update the endpoint data."""
        self.data = data

        # Remove stale values
        self.values = {
            value_id: val for value_id, val in self.values.items() if value_id in values
        }

        # Populate new values
        for value_id, value in values.items():
            if value_id not in self.values:
                self.values[value_id] = value

    def get_command_class_values(
        self, command_class: CommandClass
    ) -> dict[str, ConfigurationValue | Value]:
        """Return all values for a given command class."""
        return {
            value_id: value
            for value_id, value in self.values.items()
            if value.command_class == command_class
        }

    def get_configuration_values(self) -> dict[str, ConfigurationValue]:
        """Return all configuration values for an endpoint."""
        return cast(
            dict[str, ConfigurationValue],
            self.get_command_class_values(CommandClass.CONFIGURATION),
        )

    async def async_send_command(
        self,
        cmd: str,
        require_schema: int | None = None,
        wait_for_result: bool | None = None,
        **cmd_kwargs: Any,
    ) -> dict[str, Any] | None:
        """
        Send an endpoint command. For internal use only.

        If wait_for_result is not None, it will take precedence, otherwise we will
        decide to wait or not based on the node status.
        """
        if self.client.driver is None:
            raise FailedCommand(
                "Command failed", "failed_command", "The client is not connected"
            )
        kwargs = {}
        message = {
            "command": f"endpoint.{cmd}",
            "nodeId": self.node_id,
            "endpoint": self.index,
            **cmd_kwargs,
        }
        if require_schema is not None:
            kwargs["require_schema"] = require_schema

        if wait_for_result:
            result = await self.client.async_send_command(message, **kwargs)
            return result

        if wait_for_result is None and self.node.status not in (
            NodeStatus.ASLEEP,
            NodeStatus.DEAD,
        ):
            result_task = asyncio.create_task(
                self.client.async_send_command(message, **kwargs)
            )
            status_task = asyncio.create_task(self.node.status_event.wait())
            await asyncio.wait(
                [result_task, status_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            status_task.cancel()
            if self.node.status_event.is_set() and not result_task.done():
                result_task.cancel()
                return None
            return result_task.result()

        await self.client.async_send_command_no_wait(message, **kwargs)
        return None

    async def async_invoke_cc_api(
        self,
        command_class: CommandClass,
        method_name: str,
        *args: Any,
        wait_for_result: bool | None = None,
    ) -> Any:
        """Call endpoint.invoke_cc_api command."""
        if not any(cc.id == command_class.value for cc in self.command_classes):
            raise NotFoundError(
                f"Command class {command_class} not found on endpoint {self}"
            )
        result = await self.async_send_command(
            "invoke_cc_api",
            commandClass=command_class.value,
            methodName=method_name,
            args=list(args),
            require_schema=7,
            wait_for_result=wait_for_result,
        )
        if not result:
            return None
        return result["response"]

    async def async_supports_cc_api(self, command_class: CommandClass) -> bool:
        """Call endpoint.supports_cc_api command."""
        result = await self.async_send_command(
            "supports_cc_api",
            commandClass=command_class.value,
            require_schema=7,
            wait_for_result=True,
        )
        assert result
        return cast(bool, result["supported"])

    async def async_supports_cc(self, command_class: CommandClass) -> bool:
        """Call endpoint.supports_cc command."""
        result = await self.async_send_command(
            "supports_cc",
            commandClass=command_class.value,
            require_schema=23,
            wait_for_result=True,
        )
        assert result
        return cast(bool, result["supported"])

    async def async_controls_cc(self, command_class: CommandClass) -> bool:
        """Call endpoint.controls_cc command."""
        result = await self.async_send_command(
            "controls_cc",
            commandClass=command_class.value,
            require_schema=23,
            wait_for_result=True,
        )
        assert result
        return cast(bool, result["controlled"])

    async def async_is_cc_secure(self, command_class: CommandClass) -> bool:
        """Call endpoint.is_cc_secure command."""
        result = await self.async_send_command(
            "is_cc_secure",
            commandClass=command_class.value,
            require_schema=23,
            wait_for_result=True,
        )
        assert result
        return cast(bool, result["secure"])

    async def async_get_cc_version(self, command_class: CommandClass) -> bool:
        """Call endpoint.get_cc_version command."""
        result = await self.async_send_command(
            "get_cc_version",
            commandClass=command_class.value,
            require_schema=23,
            wait_for_result=True,
        )
        assert result
        return cast(bool, result["version"])

    async def async_get_node_unsafe(self) -> NodeDataType:
        """Call endpoint.get_node_unsafe command."""
        result = await self.async_send_command(
            "get_node_unsafe",
            require_schema=23,
            wait_for_result=True,
        )
        assert result
        return cast("NodeDataType", result["node"])

    async def async_set_raw_config_parameter_value(
        self,
        new_value: int | str,
        property_: int | str,
        property_key: int | None = None,
        value_size: Literal[1, 2, 4] | None = None,
        value_format: ConfigurationValueFormat | None = None,
    ) -> tuple[Value, SetConfigParameterResult]:
        """Send setRawConfigParameterValue."""
        try:
            zwave_value = next(
                config_value
                for config_value in self.get_configuration_values().values()
                if property_
                == (
                    config_value.property_name
                    if isinstance(property_, str)
                    else config_value.property_
                )
                and property_key == config_value.property_key
            )
        except StopIteration:
            raise NotFoundError(
                f"Configuration parameter with parameter {property_} and bitmask "
                f"{property_key} on node {self} could not be found"
            ) from None

        if not isinstance(new_value, str):
            value = new_value
        else:
            try:
                value = int(
                    next(
                        k
                        for k, v in zwave_value.metadata.states.items()
                        if v == new_value
                    )
                )
            except StopIteration:
                raise NotFoundError(
                    f"Configuration parameter {zwave_value.value_id} does not have "
                    f"{new_value} as a valid state. If this is a valid call, you must "
                    "use the state key instead of the string."
                ) from None

        if (value_size is not None and value_format is None) or (
            value_size is None and value_format is not None
        ):
            raise ValueError(
                "value_size and value_format must either both be included or not "
                "included"
            )

        if value_size is not None and property_key is not None:
            raise ValueError(
                "property_key can only be included when value_size and value_format "
                "are not included"
            )

        options = {
            "value": value,
            "parameter": zwave_value.property_,
            "bitMask": zwave_value.property_key,
            "valueSize": value_size,
            "valueFormat": value_format,
        }

        data = await self.async_send_command(
            "set_raw_config_parameter_value",
            options={k: v for k, v in options.items() if v is not None},
            require_schema=33,
        )

        if data is None:
            return zwave_value, SetConfigParameterResult(CommandStatus.QUEUED)

        if (result := data.get("result")) is None:
            return zwave_value, SetConfigParameterResult(CommandStatus.ACCEPTED)

        return zwave_value, SetConfigParameterResult(
            CommandStatus.ACCEPTED, SupervisionResult(result)
        )
