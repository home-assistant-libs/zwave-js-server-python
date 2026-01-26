"""Provide a model for the Z-Wave JS Driver."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal, cast

from zwave_js_server.model.firmware import (
    FirmwareUpdateData,
    FirmwareUpdateDataDataType,
    FirmwareUpdateInfo,
    FirmwareUpdateInfoDataType,
)

from ...event import BaseEventModel, Event, EventBase
from ..config_manager import ConfigManager
from ..controller import Controller
from ..log_config import LogConfig, LogConfigDataType
from ..log_message import LogMessage, LogMessageContextDataType, LogMessageDataType
from .firmware import (
    DriverFirmwareUpdateProgress,
    DriverFirmwareUpdateProgressDataType,
    DriverFirmwareUpdateResult,
    DriverFirmwareUpdateResultDataType,
)

if TYPE_CHECKING:
    from ...client import Client

_LOGGER = logging.getLogger(__package__)


class BaseDriverEventModel(BaseEventModel):
    """Base model for a driver event."""

    source: Literal["driver"]


class LogConfigUpdatedEventModel(BaseDriverEventModel):
    """Model for `log config updated` event data."""

    event: Literal["log config updated"]
    config: LogConfigDataType

    @classmethod
    def from_dict(cls, data: dict) -> LogConfigUpdatedEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            config=data["config"],
        )


class AllNodesReadyEventModel(BaseDriverEventModel):
    """Model for `all nodes ready` event data."""

    event: Literal["all nodes ready"]


class LoggingEventModel(BaseDriverEventModel):
    """Model for `logging` event data."""

    event: Literal["logging"]
    message: str | list[str]  # required
    formattedMessage: str | list[str]  # required
    direction: str  # required
    level: str  # required
    context: LogMessageContextDataType  # required
    primaryTags: str | None = None
    secondaryTags: str | None = None
    secondaryTagPadding: int | None = None
    multiline: bool | None = None
    timestamp: str | None = None
    label: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> LoggingEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            message=data["message"],
            formattedMessage=data["formattedMessage"],
            direction=data["direction"],
            level=data["level"],
            context=data["context"],
            primaryTags=data.get("primaryTags"),
            secondaryTags=data.get("secondaryTags"),
            secondaryTagPadding=data.get("secondaryTagPadding"),
            multiline=data.get("multiline"),
            timestamp=data.get("timestamp"),
            label=data.get("label"),
        )


class DriverReadyEventModel(BaseDriverEventModel):
    """Model for `driver ready` event data."""

    event: Literal["driver ready"]


class FirmwareUpdateFinishedEventModel(BaseDriverEventModel):
    """Model for `firmware update finished` event data."""

    event: Literal["firmware update finished"]
    result: DriverFirmwareUpdateResultDataType

    @classmethod
    def from_dict(cls, data: dict) -> FirmwareUpdateFinishedEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            result=data["result"],
        )


class FirmwareUpdateProgressEventModel(BaseDriverEventModel):
    """Model for `firmware update progress` event data."""

    event: Literal["firmware update progress"]
    progress: DriverFirmwareUpdateProgressDataType

    @classmethod
    def from_dict(cls, data: dict) -> FirmwareUpdateProgressEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            progress=data["progress"],
        )


class ErrorEventModel(BaseDriverEventModel):
    """Model for `error` event data."""

    event: Literal["error"]
    error: str

    @classmethod
    def from_dict(cls, data: dict) -> ErrorEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            error=data["error"],
        )


class BootloaderReadyEventModel(BaseDriverEventModel):
    """Model for `bootloader ready` event data."""

    event: Literal["bootloader ready"]


DRIVER_EVENT_MODEL_MAP: dict[str, type[BaseDriverEventModel]] = {
    "all nodes ready": AllNodesReadyEventModel,
    "bootloader ready": BootloaderReadyEventModel,
    "error": ErrorEventModel,
    "log config updated": LogConfigUpdatedEventModel,
    "logging": LoggingEventModel,
    "driver ready": DriverReadyEventModel,
    "firmware update finished": FirmwareUpdateFinishedEventModel,
    "firmware update progress": FirmwareUpdateProgressEventModel,
}


class CheckConfigUpdates:
    """Represent config updates check."""

    def __init__(self, data: dict) -> None:
        """Initialize class."""
        self.installed_version: str = data["installedVersion"]
        self.update_available: bool = data["updateAvailable"]
        self.new_version: str | None = data.get("newVersion")


class Driver(EventBase):
    """Represent a Z-Wave JS driver."""

    def __init__(
        self, client: Client, state: dict, log_config: LogConfigDataType
    ) -> None:
        """Initialize driver."""
        super().__init__()
        self.client = client
        self._state = state
        self.controller = Controller(client, state)
        self.log_config = LogConfig.from_dict(log_config)
        self.config_manager = ConfigManager(client)
        self._firmware_update_progress: DriverFirmwareUpdateProgress | None = None

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.controller)

    def __eq__(self, other: object) -> bool:
        """Return whether this instance equals another."""
        if not isinstance(other, Driver):
            return False
        return self.controller == other.controller

    @property
    def firmware_update_progress(self) -> DriverFirmwareUpdateProgress | None:
        """Return firmware update progress."""
        return self._firmware_update_progress

    # Schema 45+ state properties

    @property
    def ready(self) -> bool | None:
        """Return whether the driver is ready."""
        return self._state.get("driver", {}).get("ready")

    @property
    def all_nodes_ready(self) -> bool | None:
        """Return whether all nodes are ready."""
        return self._state.get("driver", {}).get("allNodesReady")

    @property
    def config_version(self) -> str | None:
        """Return device config database version."""
        return self._state.get("driver", {}).get("configVersion")

    def receive_event(self, event: Event) -> None:
        """Receive an event."""
        if event.data["source"] != "driver":
            self.controller.receive_event(event)
            return

        if (event_type := event.type) not in DRIVER_EVENT_MODEL_MAP:
            _LOGGER.info("Unhandled driver event: %s", event_type)
            return

        DRIVER_EVENT_MODEL_MAP[event_type].from_dict(event.data)
        self._handle_event_protocol(event)

        self.emit(event_type, event.data)

    async def _async_send_command(
        self, command: str, require_schema: int | None = None, **kwargs: Any
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

    async def async_firmware_update_otw(
        self,
        *,
        update_data: FirmwareUpdateData | None = None,
        update_info: FirmwareUpdateInfo | None = None,
    ) -> DriverFirmwareUpdateResult:
        """Send firmwareUpdateOTW command to Driver."""
        if update_data is None and update_info is None:
            raise ValueError(
                "Either update_data or update_info must be provided for firmware update."
            )
        if update_data is not None and update_info is not None:
            raise ValueError(
                "Only one of update_data or update_info can be provided for firmware update."
            )
        params: FirmwareUpdateDataDataType | dict[str, FirmwareUpdateInfoDataType]
        if update_data is not None:
            params = update_data.to_dict()
        elif update_info is not None:
            params = {"updateInfo": update_info.to_dict()}
        data = await self._async_send_command(
            "firmware_update_otw", require_schema=44, **params
        )
        return DriverFirmwareUpdateResult(data["result"])

    async def async_is_otw_firmware_update_in_progress(self) -> bool:
        """Send isOTWFirmwareUpdateInProgress command to Driver."""
        result = await self._async_send_command(
            "is_otw_firmware_update_in_progress", require_schema=41
        )
        return cast(bool, result["progress"])

    async def async_set_preferred_scales(
        self, scales: dict[str | int, str | int]
    ) -> None:
        """Send command to set preferred sensor scales."""
        await self._async_send_command(
            "set_preferred_scales", scales=scales, require_schema=6
        )

    async def async_hard_reset(self) -> None:
        """Send command to hard reset controller."""
        await self._async_send_command("hard_reset", require_schema=25)

    async def async_try_soft_reset(self) -> None:
        """Send command to try to soft reset controller."""
        await self._async_send_command("try_soft_reset", require_schema=25)

    async def async_soft_reset(self) -> None:
        """Send command to soft reset controller."""
        await self._async_send_command("soft_reset", require_schema=25)

    async def async_shutdown(self) -> bool:
        """Send command to shutdown controller."""
        data = await self._async_send_command("shutdown", require_schema=27)
        return cast(bool, data["success"])

    async def async_soft_reset_and_restart(self) -> None:
        """Soft reset the controller and restart the driver."""
        await self._async_send_command("soft_reset_and_restart", require_schema=45)

    async def async_enter_bootloader(self) -> None:
        """Put the controller into bootloader mode."""
        await self._async_send_command("enter_bootloader", require_schema=45)

    async def async_leave_bootloader(self) -> None:
        """Exit bootloader mode."""
        await self._async_send_command("leave_bootloader", require_schema=45)

    async def async_get_supported_cc_version(
        self, node_id: int, cc: int, endpoint: int = 0
    ) -> int | None:
        """Get the supported CC version for a node/endpoint."""
        data = await self._async_send_command(
            "get_supported_cc_version",
            nodeId=node_id,
            commandClass=cc,
            endpointIndex=endpoint,
            require_schema=45,
        )
        return cast(int | None, data.get("version"))

    async def async_get_safe_cc_version(
        self, node_id: int, cc: int, endpoint: int = 0
    ) -> int | None:
        """Get a safe CC version (returns 1 if unknown, None if not implemented)."""
        data = await self._async_send_command(
            "get_safe_cc_version",
            nodeId=node_id,
            commandClass=cc,
            endpointIndex=endpoint,
            require_schema=45,
        )
        return cast(int | None, data.get("version"))

    async def async_update_user_agent(self, components: dict[str, str]) -> None:
        """Update user agent components for service requests."""
        await self._async_send_command(
            "update_user_agent",
            components=components,
            require_schema=45,
        )

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

    def handle_driver_ready(self, event: Event) -> None:
        """Process a driver ready event."""

    def handle_firmware_update_progress(self, event: Event) -> None:
        """Process a firmware update progress event."""
        self._firmware_update_progress = event.data["firmware_update_progress"] = (
            DriverFirmwareUpdateProgress(event.data["progress"])
        )

    def handle_firmware_update_finished(self, event: Event) -> None:
        """Process a firmware update finished event."""
        self._firmware_update_progress = None
        event.data["firmware_update_finished"] = DriverFirmwareUpdateResult(
            event.data["result"]
        )

    def handle_error(self, event: Event) -> None:
        """Process a driver error event."""
        # Error message is already in event.data["error"]

    def handle_bootloader_ready(self, event: Event) -> None:
        """Process a bootloader ready event."""
        # No additional processing needed
