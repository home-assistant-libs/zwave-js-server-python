"""Constants for the Battery CC."""

from __future__ import annotations

from enum import IntEnum


class BatteryReplacementStatus(IntEnum):
    """Enum with all (known/used) Z-Wave Battery Replacement Statuses."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/cc/src/lib/_Types.ts#L328
    NO = 0
    SOON = 1
    NOW = 2
