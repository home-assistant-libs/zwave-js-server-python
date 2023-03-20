"""Constants for the Color Switch CC."""
from __future__ import annotations

from enum import IntEnum


class ColorComponent(IntEnum):
    """Enum with all (known/used) Color Switch CC colors."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/ColorSwitchCC.ts#L62
    WARM_WHITE = 0
    COLD_WHITE = 1
    RED = 2
    GREEN = 3
    BLUE = 4
    AMBER = 5
    CYAN = 6
    PURPLE = 7
    INDEX = 8


# Keys for the Color Switch CC combined colors value
# https://github.com/zwave-js/node-zwave-js/pull/1782
COLOR_SWITCH_COMBINED_RED = "red"
COLOR_SWITCH_COMBINED_GREEN = "green"
COLOR_SWITCH_COMBINED_BLUE = "blue"
COLOR_SWITCH_COMBINED_AMBER = "amber"
COLOR_SWITCH_COMBINED_CYAN = "cyan"
COLOR_SWITCH_COMBINED_PURPLE = "purple"
COLOR_SWITCH_COMBINED_WARM_WHITE = "warmWhite"
COLOR_SWITCH_COMBINED_COLD_WHITE = "coldWhite"

CURRENT_COLOR_PROPERTY = "currentColor"
TARGET_COLOR_PROPERTY = "targetColor"
