"""Constants for the Battery CC."""

from __future__ import annotations

from enum import IntEnum, StrEnum


class BatteryNotificationEventType(StrEnum):
    """Enum with all (known/used) Z-Wave Battery CC Notification Event Types."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/CCHandlers/BatteryCC.ts#L24
    BATTERY_LOW = "battery low"


class BatteryReplacementStatus(IntEnum):
    """Enum with all (known/used) Z-Wave Battery Replacement Statuses."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/cc/src/lib/_Types.ts#L328
    NO = 0
    SOON = 1
    NOW = 2
