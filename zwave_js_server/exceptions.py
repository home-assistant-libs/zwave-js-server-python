"""Exceptions for zwave-js-server."""


class BaseZwaveJSServerError(Exception):
    """Base Zwave JS Server exception."""


class NotFoundError(BaseZwaveJSServerError):
    """Exception that is raised when an entity can't be found."""


class NotConnected(BaseZwaveJSServerError):
    """Exception raised when trying to handle unknown handler."""


class InvalidState(BaseZwaveJSServerError):
    """Exception raised when data gets in invalid state."""


class InvalidServerVersion(BaseZwaveJSServerError):
    """Exception raised when connected to server with incompatible version."""


class FailedCommand(BaseZwaveJSServerError):
    """When a command has failed."""

    def __init__(self, message_id: str, error_code: str):
        """Initialize a failed command error."""
        super().__init__(f"Command failed: {error_code}")
        self.message_id = message_id
        self.error_code = error_code
