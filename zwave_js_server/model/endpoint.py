"""
Model for a Zwave Node's endpoints.

https://zwave-js.github.io/node-zwave-js/#/api/endpoint?id=endpoint-properties
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, TypedDict, Union, cast

from ..const import NodeStatus
from ..event import EventBase
from ..exceptions import FailedCommand
from .command_class import CommandClass
from .device_class import DeviceClass, DeviceClassDataType
from .value import ConfigurationValue, Value

if TYPE_CHECKING:
    from ..client import Client


class EndpointDataType(TypedDict, total=False):
    """Represent an endpoint data dict type."""

    nodeId: int  # required
    index: int  # required
    deviceClass: DeviceClassDataType  # required
    installerIcon: int
    userIcon: int


class Endpoint(EventBase):
    """Model for a Zwave Node's endpoint."""

    def __init__(
        self,
        client: "Client",
        data: EndpointDataType,
        values: Dict[str, Union[ConfigurationValue, Value]] = None,
    ) -> None:
        """Initialize."""
        super().__init__()
        self.client = client
        self.data = data
        if values is not None:
            self.values = values

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

    async def _async_send_command(
        self,
        cmd: str,
        require_schema: Optional[int] = None,
        wait_for_result: Optional[bool] = None,
        **cmd_kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Send an endpoint command. For internal use only.

        If wait_for_result is not None, it will take precedence, otherwise we will decide to wait
        or not based on the node status.
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
        wait_for_result: bool = None,
    ) -> Any:
        """Call endpoint.invoke_cc_api command."""
        result = await self._async_send_command(
            "invoke_cc_api",
            commandClass=command_class.value,
            methodName=method_name,
            args=list(args),
            require_schema=7,
            wait_for_result=wait_for_result,
        )
        if result is None:
            return None
        return result["response"]

    async def async_supports_cc_api(self, command_class: CommandClass) -> bool:
        """Call endpoint.supports_cc_api command."""
        result = await self._async_send_command(
            "supports_cc_api",
            commandClass=command_class.value,
            require_schema=7,
            wait_for_result=True,
        )
        assert result
        return cast(bool, result["supported"])
