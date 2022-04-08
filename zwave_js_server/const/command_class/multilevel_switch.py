"""Constants for the Multilevel Switch CC."""
from enum import IntEnum

COVER_OPEN_PROPERTY = "Open"
COVER_UP_PROPERTY = "Up"
COVER_ON_PROPERTY = "On"
COVER_CLOSE_PROPERTY = "Close"
COVER_DOWN_PROPERTY = "Down"
COVER_OFF_PROPERTY = "Off"


class MultilevelSwitchCommand(IntEnum):
    """Enum for known multilevel switch notifications."""

    START_LEVEL_CHANGE = 4
    STOP_LEVEL_CHANGE = 5
