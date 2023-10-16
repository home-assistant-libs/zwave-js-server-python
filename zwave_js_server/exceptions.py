"""Exceptions for zwave-js-server."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .const import RssiError

if TYPE_CHECKING:
    from .const import CommandClass
    from .model.value import Value
    from .model.version import VersionInfo


class BaseZwaveJSServerError(Exception):
    """Base Zwave JS Server exception."""


class TransportError(BaseZwaveJSServerError):
    """Exception raised to represent transport errors."""

    def __init__(self, message: str, error: Exception | None = None) -> None:
        """Initialize a transport error."""
        super().__init__(message)
        self.error = error


class ConnectionClosed(TransportError):
    """Exception raised when the connection is closed."""


class CannotConnect(TransportError):
    """Exception raised when failed to connect the client."""

    def __init__(self, error: Exception) -> None:
        """Initialize a cannot connect error."""
        super().__init__(f"{error}", error)


class ConnectionFailed(TransportError):
    """Exception raised when an established connection fails."""

    def __init__(self, error: Exception | None = None) -> None:
        """Initialize a connection failed error."""
        if error is None:
            super().__init__("Connection failed.")
            return
        super().__init__(f"{error}", error)


class NotFoundError(BaseZwaveJSServerError):
    """Exception that is raised when an entity can't be found."""


class NotConnected(BaseZwaveJSServerError):
    """Exception raised when not connected to client."""


class InvalidState(BaseZwaveJSServerError):
    """Exception raised when data gets in invalid state."""


class InvalidMessage(BaseZwaveJSServerError):
    """Exception raised when an invalid message is received."""


class InvalidServerVersion(BaseZwaveJSServerError):
    """Exception raised when connected to server with incompatible version."""

    def __init__(
        self,
        version_info: VersionInfo,
        required_schema_version: int,
        message: str,
    ) -> None:
        """Initialize an invalid server version error."""
        self.server_version = version_info.server_version
        self.server_max_schema_version = version_info.max_schema_version
        self.required_schema_version = required_schema_version
        super().__init__(message)


class FailedCommand(BaseZwaveJSServerError):
    """When a command has failed."""

    def __init__(
        self, message_id: str, error_code: str, msg: str | None = None
    ) -> None:
        """Initialize a failed command error."""
        super().__init__(
            f"{error_code}: {msg}" if msg else f"Command failed: {error_code}"
        )
        self.message_id = message_id
        self.error_code = error_code


class FailedZWaveCommand(FailedCommand):
    """When a command has failed because of Z-Wave JS error."""

    def __init__(
        self, message_id: str, zwave_error_code: int, zwave_error_message: str
    ):
        """Initialize a failed command error."""
        super().__init__(
            message_id,
            "zwave_error",
            f"Z-Wave error {zwave_error_code} - {zwave_error_message}",
        )
        self.zwave_error_code = zwave_error_code
        self.zwave_error_message = zwave_error_message


class UnparseableValue(BaseZwaveJSServerError):
    """Exception raised when a value can't be parsed."""


class UnwriteableValue(BaseZwaveJSServerError):
    """Exception raised when trying to change a read only Value."""


class InvalidNewValue(BaseZwaveJSServerError):
    """Exception raised when target new value is invalid based on Value metadata."""


class ValueTypeError(BaseZwaveJSServerError):
    """Exception raised when target Zwave value is the wrong type."""


class SetValueFailed(BaseZwaveJSServerError):
    """
    Exception raise when setting a value fails.

    Refer to https://zwave-js.github.io/node-zwave-js/#/api/node?id=setvalue for
    possible reasons.
    """


class BulkSetConfigParameterFailed(BaseZwaveJSServerError):
    """
    Exception raised when bulk setting a config parameter fails.

    Derived from another exception.
    """


class InvalidCommandClass(BaseZwaveJSServerError):
    """Exception raised when Zwave Value has an invalid command class."""

    def __init__(self, value: Value, command_class: CommandClass) -> None:
        """Initialize an invalid Command Class error."""
        self.value = value
        self.command_class = command_class
        super().__init__(
            f"Value {value} does not match expected command class: {command_class}"
        )


class UnknownValueData(BaseZwaveJSServerError):
    """
    Exception raised when Zwave Value has data that the library can't parse.

    This can be caused by an upstream issue with the driver, or missing support in the
    library.
    """

    def __init__(self, value: Value, path: str) -> None:
        """Initialize an unknown data error."""
        self.value = value
        self.path = path
        super().__init__(
            f"Value {value} has unknown data in the following location: {path}. "
            f"A reinterview of node {value.node} may correct this issue, but if it "
            "doesn't, please report this issue as it may be caused by either an "
            "upstream issue with the driver or missing support for this data in the "
            "library"
        )


class RssiErrorReceived(BaseZwaveJSServerError):
    """Exception raised when an RSSI error is received."""

    def __init__(self, error: RssiError) -> None:
        """Initialize an RSSI error."""
        self.error = error
        super().__init__()


class RepeaterRssiErrorReceived(BaseZwaveJSServerError):
    """Exception raised when an RSSI error is received in list of RSSIs."""

    def __init__(self, rssi_list: list[int]) -> None:
        """Initialize an RSSI error."""
        self.rssi_list = rssi_list
        rssi_errors = [item.value for item in RssiError]
        self.error_list = [
            RssiError(rssi_) if rssi_ in rssi_errors else None for rssi_ in rssi_list
        ]
        super().__init__()
