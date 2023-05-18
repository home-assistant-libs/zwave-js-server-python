"""Constants for the Multilevel Switch CC."""
from __future__ import annotations

from enum import IntEnum

SET_TO_PREVIOUS_VALUE = 255

COVER_OPEN_PROPERTY = "Open"
COVER_UP_PROPERTY = "Up"
COVER_ON_PROPERTY = "On"
COVER_CLOSE_PROPERTY = "Close"
COVER_DOWN_PROPERTY = "Down"
COVER_OFF_PROPERTY = "Off"


class CoverStates(IntEnum):
    """Enum with all (known/used) Z-Wave Cover States."""

    CLOSED = 0
    OPEN = 99


class MultilevelSwitchCommand(IntEnum):
    """Enum for known multilevel switch notifications."""

    START_LEVEL_CHANGE = 4
    STOP_LEVEL_CHANGE = 5
