"""
Constants for the Humidity Control CCs.

Includes Humidity Control Mode, Humidity Control Operating State,
and Humidity Control Setpoint CCs.
"""
from __future__ import annotations

from enum import IntEnum

HUMIDITY_CONTROL_MODE_PROPERTY = "mode"
HUMIDITY_CONTROL_OPERATING_STATE_PROPERTY = "state"
HUMIDITY_CONTROL_SETPOINT_PROPERTY = "setpoint"
HUMIDITY_CONTROL_SETPOINT_SCALE_PROPERTY = "setpointScale"
HUMIDITY_CONTROL_SUPPORTED_SETPOINT_TYPES_PROPERTY = "supportedSetpointTypes"


class HumidityControlMode(IntEnum):
    """Enum with all (known/used) Z-Wave HumidityControlModes."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/HumidityControlModeCC.ts
    OFF = 0
    HUMIDIFY = 1
    DEHUMIDIFY = 2
    AUTO = 3


class HumidityControlOperatingState(IntEnum):
    """Enum with all (known/used) Z-Wave Humidity Control OperatingStates."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/HumidityControlOperatingStateCC.ts
    IDLE = 0
    HUMIDIFYING = 1
    DEHUMIDIFYING = 2


class HumidityControlSetpointType(IntEnum):
    """
    Enum with all (known/used) Z-Wave Humidity Control Setpoint Types.

    Returns tuple of (property_key, property_key_name).
    """

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/HumidityControlSetpointCC.ts
    NA = 0
    HUMIDIFIER = 1
    DEHUMIDIFIER = 2
    AUTO = 3


HUMIDITY_CONTROL_MODE_SETPOINT_MAP: dict[int, list[HumidityControlSetpointType]] = {
    HumidityControlMode.OFF: [],
    HumidityControlMode.HUMIDIFY: [HumidityControlSetpointType.HUMIDIFIER],
    HumidityControlMode.DEHUMIDIFY: [HumidityControlSetpointType.DEHUMIDIFIER],
    HumidityControlMode.AUTO: [
        HumidityControlSetpointType.HUMIDIFIER,
        HumidityControlSetpointType.DEHUMIDIFIER,
    ],
}
