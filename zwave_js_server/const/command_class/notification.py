"""Constants for the Notification CC."""
from __future__ import annotations

from enum import IntEnum

CC_SPECIFIC_NOTIFICATION_TYPE = "notificationType"


class NotificationType(IntEnum):
    """Enum with all (known/used) Z-Wave notification types."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/notifications.json
    SMOKE_ALARM = 1
    CARBON_MONOXIDE_ALARM = 2
    CARBON_DIOXIDE_ALARM = 3
    HEAT_ALARM = 4
    WATER_ALARM = 5
    ACCESS_CONTROL = 6
    HOME_SECURITY = 7
    POWER_MANAGEMENT = 8
    SYSTEM = 9
    EMERGENCY = 10
    CLOCK = 11
    APPLIANCE = 12
    HOME_HEALTH = 13
    SIREN = 14
    WATER_VALVE = 15
    WEATHER_ALARM = 16
    IRRIGATION = 17
    GAS = 18
    PEST_CONTROL = 19
    LIGHT_SENSOR = 20
    WATER_QUALITY_MONITORING = 21
    HOME_MONITORING = 22
