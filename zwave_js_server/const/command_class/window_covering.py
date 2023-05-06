"""Constants for the Barrier Operator CC."""
from __future__ import annotations

from enum import Enum, IntEnum


class WindowCoveringPropertyKey(str, Enum):
    """Enum of all known Window Covering CC property keys."""

    HORIZONTAL_SLATS_ANGLE = "Horizontal Slats Angle"
    HORIZONTAL_SLATS_ANGLE_NO_POSITION = "Horizontal Slats Angle (no position)"
    INBOUND_BOTTOM = "Inbound Bottom"
    INBOUND_BOTTOM_NO_POSITION = "Inbound Bottom (no position)"
    INBOUND_LEFT = "Inbound Left"
    INBOUND_LEFT_NO_POSITION = "Inbound Left (no position)"
    INBOUND_LEFT_RIGHT = "Inbound Left/Right"
    INBOUND_LEFT_RIGHT_NO_POSITION = "Inbound Left/Right (no position)"
    INBOUND_RIGHT = "Inbound Right"
    INBOUND_RIGHT_NO_POSITION = "Inbound Right (no position)"
    INBOUND_TOP = "Inbound Top"
    INBOUND_TOP_NO_POSITION = "Inbound Top (no position)"
    INBOUND_TOP_BOTTOM = "Inbound Top/Bottom"
    INBOUND_TOP_BOTTOM_NO_POSITION = "Inbound Top/Bottom (no position)"
    OUTBOUND_BOTTOM = "Outbound Bottom"
    OUTBOUND_BOTTOM_NO_POSITION = "Outbound Bottom (no position)"
    OUTBOUND_LEFT = "Outbound Left"
    OUTBOUND_LEFT_NO_POSITION = "Outbound Left (no position)"
    OUTBOUND_RIGHT = "Outbound Right"
    OUTBOUND_RIGHT_NO_POSITION = "Outbound Right (no position)"
    OUTBOUND_TOP = "Outbound Top"
    OUTBOUND_TOP_NO_POSITION = "Outbound Top (no position)"
    VERTICAL_SLATS_ANGLE = "Vertical Slats Angle"
    VERTICAL_SLATS_ANGLE_NO_POSITION = "Vertical Slats Angle (no position)"


class SlatStates(IntEnum):
    """Enum with all (known/used) Z-Wave Slat States."""

    CLOSED_1 = 0
    OPEN = 50
    CLOSED_2 = 99


NO_POSITION_SUFFIX = "(no position)"
