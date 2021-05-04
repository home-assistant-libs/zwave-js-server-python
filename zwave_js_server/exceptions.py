"""Exceptions for zwave-js-server."""


from typing import Optional


class BaseZwaveJSServerError(Exception):
    """Base Zwave JS Server exception."""


class TransportError(BaseZwaveJSServerError):
    """Exception raised to represent transport errors."""

    def __init__(self, message: str, error: Optional[Exception] = None) -> None:
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

    def __init__(self, error: Optional[Exception] = None) -> None:
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


class FailedCommand(BaseZwaveJSServerError):
    """When a command has failed."""

    def __init__(self, message_id: str, error_code: str, msg: Optional[str] = None):
        """Initialize a failed command error."""
        super().__init__(msg or f"Command failed: {error_code}")
        self.message_id = message_id
        self.error_code = error_code


class FailedZWaveCommand(FailedCommand):
    """When a command has failed because of Z-Wave JS error."""

    def __init__(
        self,
        message_id: str,
        zwave_error_code: int,
        zwave_error_message: str,
    ):
        """Initialize a failed command error."""
        super().__init__(
            message_id,
            "zwave_error",
            f"Z-Wave error {zwave_error_code}: {zwave_error_message}",
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

    Derived from another exception
    """
