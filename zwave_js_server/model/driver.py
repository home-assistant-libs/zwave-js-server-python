"""Provide a model for the Z-Wave JS Driver."""
from typing import Any, Dict, Optional, TYPE_CHECKING, Union, cast

from zwave_js_server.model.log_config import LogConfig, LogConfigDataType
from zwave_js_server.model.log_message import LogMessage, LogMessageDataType

from ..event import Event, EventBase
from .controller import Controller

if TYPE_CHECKING:
    from ..client import Client


class CheckConfigUpdates:
    """Represent config updates check."""

    def __init__(self, data: dict) -> None:
        """Initialize class."""
        self.update_available: bool = data["updateAvailable"]
        self.new_version: Optional[str] = data.get("newVersion")


class Driver(EventBase):
    """Represent a Z-Wave JS driver."""

    def __init__(
        self, client: "Client", state: dict, log_config: LogConfigDataType
    ) -> None:
        """Initialize driver."""
        super().__init__()
        self.client = client
        self.controller = Controller(client, state)
        self.log_config = LogConfig.from_dict(log_config)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.controller)

    def __eq__(self, other: object) -> bool:
        """Return whether this instance equals another."""
        if not isinstance(other, Driver):
            return False
        return self.controller == other.controller

    def receive_event(self, event: Event) -> None:
        """Receive an event."""
        if event.data["source"] != "driver":
            self.controller.receive_event(event)
            return

        self._handle_event_protocol(event)

        self.emit(event.type, event.data)

    def handle_logging(self, event: Event) -> None:
        """Process a driver logging event."""
        event.data["log_message"] = LogMessage(cast(LogMessageDataType, event.data))

    def handle_log_config_updated(self, event: Event) -> None:
        """Process a driver log config updated event."""
        event.data["log_config"] = self.log_config = LogConfig.from_dict(
            event.data["config"]
        )

    def handle_all_nodes_ready(self, event: Event) -> None:
        """Process a driver all nodes ready event."""

    async def _async_send_command(
        self, command: str, require_schema: int = None, **kwargs: Any
    ) -> dict:
        """Send a driver command. For internal use only."""
        return await self.client.async_send_command(
            {
                "command": f"driver.{command}",
                **kwargs,
            },
            require_schema,
        )

    async def async_update_log_config(self, log_config: LogConfig) -> None:
        """Update log config for driver."""
        await self._async_send_command(
            "update_log_config", config=log_config.to_dict(), require_schema=4
        )

    async def async_get_log_config(self) -> LogConfig:
        """Return current log config for driver."""
        result = await self._async_send_command("get_log_config", require_schema=4)
        return LogConfig.from_dict(result["config"])

    async def async_start_listening_logs(self) -> None:
        """Send command to start listening to log events."""
        await self._async_send_command("start_listening_logs", require_schema=4)

    async def async_stop_listening_logs(self) -> None:
        """Send command to stop listening to log events."""
        await self._async_send_command("stop_listening_logs", require_schema=4)

    async def async_enable_statistics(
        self, application_name: str, application_version: str
    ) -> None:
        """Send command to enable data collection."""
        await self._async_send_command(
            "enable_statistics",
            applicationName=application_name,
            applicationVersion=application_version,
            require_schema=4,
        )

    async def async_disable_statistics(self) -> None:
        """Send command to stop listening to log events."""
        await self._async_send_command("disable_statistics", require_schema=4)

    async def async_is_statistics_enabled(self) -> bool:
        """Send command to start listening to log events."""
        result = await self._async_send_command(
            "is_statistics_enabled", require_schema=4
        )
        return cast(bool, result["statisticsEnabled"])

    async def async_check_for_config_updates(self) -> CheckConfigUpdates:
        """Send command to check for config updates."""
        result = await self._async_send_command(
            "check_for_config_updates", require_schema=5
        )
        return CheckConfigUpdates(result)

    async def async_install_config_update(self) -> bool:
        """Send command to install config update."""
        result = await self._async_send_command(
            "install_config_update", require_schema=5
        )
        return cast(bool, result["success"])

    async def async_set_preferred_scales(
        self, scales: Dict[Union[str, int], Union[str, int]]
    ) -> None:
        """Send command to set preferred sensor scales."""
        await self._async_send_command(
            "set_preferred_scales", scales=scales, require_schema=6
        )
