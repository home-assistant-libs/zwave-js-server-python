"""Provide exceptions for zwave-js-server."""


class ZWaveJSServerError(Exception):
    """Represent the base zwave-js-server exception."""


class InvalidMessageError(ZWaveJSServerError):
    """Represent an invalid websocket message exception."""


class MissingNodeError(ZWaveJSServerError):
    """Represent a missing node exception."""
