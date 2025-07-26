"""Provide a model for Z-Wave driver firmware."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from zwave_js_server.model.firmware import (
    FirmwareUpdateData,
    FirmwareUpdateDataDataType,
    FirmwareUpdateProgress,
    FirmwareUpdateProgressDataType,
    FirmwareUpdateResult,
    FirmwareUpdateResultDataType,
)


class DriverFirmwareUpdateDataDataType(FirmwareUpdateDataDataType):
    """Represent a driver firmware update data dict type."""


@dataclass
class DriverFirmwareUpdateData(FirmwareUpdateData):
    """Driver firmware update data."""


class DriverFirmwareUpdateStatus(IntEnum):
    """Enum with all driver firmware update status values.

    https://zwave-js.github.io/node-zwave-js/#/api/driver?id=quotfirmware-update-finishedquot
    """

    ERROR_TIMEOUT = 0
    # The maximum number of retry attempts for a firmware fragments were reached
    ERROR_RETRY_LIMIT_REACHED = 1
    # The update was aborted by the bootloader
    ERROR_ABORTED = 2
    # This driver does not support firmware updates
    ERROR_NOT_SUPPORTED = 3
    OK = 255


class DriverFirmwareUpdateProgressDataType(FirmwareUpdateProgressDataType):
    """Represent a driver firmware update progress dict type."""


@dataclass
class DriverFirmwareUpdateProgress(FirmwareUpdateProgress):
    """Model for a driver firmware update progress data."""

    data: DriverFirmwareUpdateProgressDataType = field(repr=False)


class DriverFirmwareUpdateResultDataType(FirmwareUpdateResultDataType):
    """Represent a driver firmware update result dict type."""


@dataclass
class DriverFirmwareUpdateResult(FirmwareUpdateResult):
    """Model for driver firmware update result data."""

    data: DriverFirmwareUpdateResultDataType = field(repr=False)
    status: DriverFirmwareUpdateStatus = field(init=False)
    success: bool = field(init=False)
    _status_class = DriverFirmwareUpdateStatus
