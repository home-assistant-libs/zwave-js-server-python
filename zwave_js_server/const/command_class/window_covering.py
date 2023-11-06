"""Constants for the Barrier Operator CC."""
from __future__ import annotations

from enum import IntEnum

NO_POSITION_SUFFIX = "(no position)"
WINDOW_COVERING_LEVEL_CHANGE_DOWN_PROPERTY = "levelChangeDown"
WINDOW_COVERING_LEVEL_CHANGE_UP_PROPERTY = "levelChangeUp"


class WindowCoveringPropertyKey(IntEnum):
    """Enum of all known Window Covering CC property keys."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/cc/src/lib/_Types.ts#L1588
    OUTBOUND_LEFT_NO_POSITION = 0
    OUTBOUND_LEFT = 1
    OUTBOUND_RIGHT_NO_POSITION = 2
    OUTBOUND_RIGHT = 3
    INBOUND_LEFT_NO_POSITION = 4
    INBOUND_LEFT = 5
    INBOUND_RIGHT_NO_POSITION = 6
    INBOUND_RIGHT = 7
    INBOUND_LEFT_RIGHT_NO_POSITION = 8
    INBOUND_LEFT_RIGHT = 9
    VERTICAL_SLATS_ANGLE_NO_POSITION = 10
    VERTICAL_SLATS_ANGLE = 11
    OUTBOUND_BOTTOM_NO_POSITION = 12
    OUTBOUND_BOTTOM = 13
    OUTBOUND_TOP_NO_POSITION = 14
    OUTBOUND_TOP = 15
    INBOUND_BOTTOM_NO_POSITION = 16
    INBOUND_BOTTOM = 17
    INBOUND_TOP_NO_POSITION = 18
    INBOUND_TOP = 19
    INBOUND_TOP_BOTTOM_NO_POSITION = 20
    INBOUND_TOP_BOTTOM = 21
    HORIZONTAL_SLATS_ANGLE_NO_POSITION = 22
    HORIZONTAL_SLATS_ANGLE = 23


NO_POSITION_PROPERTY_KEYS = {
    WindowCoveringPropertyKey.OUTBOUND_LEFT_NO_POSITION,
    WindowCoveringPropertyKey.OUTBOUND_RIGHT_NO_POSITION,
    WindowCoveringPropertyKey.INBOUND_LEFT_NO_POSITION,
    WindowCoveringPropertyKey.INBOUND_RIGHT_NO_POSITION,
    WindowCoveringPropertyKey.INBOUND_LEFT_RIGHT_NO_POSITION,
    WindowCoveringPropertyKey.VERTICAL_SLATS_ANGLE_NO_POSITION,
    WindowCoveringPropertyKey.OUTBOUND_BOTTOM_NO_POSITION,
    WindowCoveringPropertyKey.OUTBOUND_TOP_NO_POSITION,
    WindowCoveringPropertyKey.INBOUND_BOTTOM_NO_POSITION,
    WindowCoveringPropertyKey.INBOUND_TOP_NO_POSITION,
    WindowCoveringPropertyKey.INBOUND_TOP_BOTTOM_NO_POSITION,
    WindowCoveringPropertyKey.HORIZONTAL_SLATS_ANGLE_NO_POSITION,
}


class SlatStates(IntEnum):
    """Enum with all (known/used) Z-Wave Slat States."""

    CLOSED_1 = 0
    OPEN = 50
    CLOSED_2 = 99
