"""Exceptions for zwave-js-server."""


class BaseZwaveJSServerError(Exception):
    """Base Zwave JS Server exception."""


class NotFoundError(BaseZwaveJSServerError):
    """Exception that is raised when an entity can't be found."""
