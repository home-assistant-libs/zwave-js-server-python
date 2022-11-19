"""
Model for a Zwave Node's endpoints.

https://zwave-js.github.io/node-zwave-js/#/api/endpoint?id=endpoint-properties
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from ..const import TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED, NodeStatus
from ..event import EventBase
from ..exceptions import FailedCommand, NotFoundError
from .command_class import CommandClass, CommandClassInfo, CommandClassInfoDataType
from .device_class import DeviceClass, DeviceClassDataType
from .value import ConfigurationValue, Value

if TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED:
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

if TYPE_CHECKING:
    from ..client import Client
    from .node.data_model import NodeDataType


class EndpointDataType(TypedDict, total=False):
    """Represent an endpoint data dict type."""

    nodeId: int  # required
    index: int  # required
    deviceClass: DeviceClassDataType  # required
    installerIcon: int
    userIcon: int
    commandClasses: List[CommandClassInfoDataType]


class Endpoint(EventBase):
    """Model for a Zwave Node's endpoint."""

    def __init__(
        self,
        client: "Client",
        data: EndpointDataType,
        values: Dict[str, Union[ConfigurationValue, Value]],
    ) -> None:
        """Initialize."""
        super().__init__()
        self.client = client
        self.data: EndpointDataType = {}
        self.values: Dict[str, Union[ConfigurationValue, Value]] = {}
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
    def device_class(self) -> DeviceClass:
        """Return the device_class."""
        return DeviceClass(self.data["deviceClass"])

    @property
    def installer_icon(self) -> Optional[int]:
        """Return installer icon property."""
        return self.data.get("installerIcon")

    @property
    def user_icon(self) -> Optional[int]:
        """Return user icon property."""
        return self.data.get("userIcon")

    @property
    def command_classes(self) -> List[CommandClassInfo]:
        """Return all CommandClasses supported on this node."""
        return [CommandClassInfo(cc) for cc in self.data["commandClasses"]]

    def update(
        self,
        data: EndpointDataType,
        values: Dict[str, Union[ConfigurationValue, Value]],
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

    async def async_send_command(
        self,
        cmd: str,
        require_schema: Optional[int] = None,
        wait_for_result: Optional[bool] = None,
        **cmd_kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Send an endpoint command. For internal use only.

        If wait_for_result is not None, it will take precedence, otherwise we will decide
        to wait or not based on the node status.
        """
        if self.client.driver is None:
            raise FailedCommand(
                "Command failed", "failed_command", "The client is not connected"
            )
        node = self.client.driver.controller.nodes[self.node_id]
        kwargs = {}
        message = {
            "command": f"endpoint.{cmd}",
            "nodeId": self.node_id,
            "endpoint": self.index,
            **cmd_kwargs,
        }
        if require_schema is not None:
            kwargs["require_schema"] = require_schema

        if wait_for_result or (
            wait_for_result is None and node.status != NodeStatus.ASLEEP
        ):
            result = await self.client.async_send_command(message, **kwargs)
            return result

        await self.client.async_send_command_no_wait(message, **kwargs)
        return None

    async def async_invoke_cc_api(
        self,
        command_class: CommandClass,
        method_name: str,
        *args: Any,
        wait_for_result: Optional[bool] = None,
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

    async def async_get_node_unsafe(self) -> "NodeDataType":
        """Call endpoint.get_node_unsafe command."""
        result = await self.async_send_command(
            "get_node_unsafe",
            require_schema=23,
            wait_for_result=True,
        )
        assert result
        return cast("NodeDataType", result["node"])
