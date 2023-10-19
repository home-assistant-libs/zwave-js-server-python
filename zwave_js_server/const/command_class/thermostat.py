"""
Constants for the Thermostat CCs.

Includes Thermostat Fan Mode, Thermostat Fan State, Thermostat Mode, Thermostat
Operating State, Thermostat Setback, and Thermostat Setpoint CCs.
"""
from __future__ import annotations

from enum import IntEnum

THERMOSTAT_MODE_PROPERTY = "mode"
THERMOSTAT_SETPOINT_PROPERTY = "setpoint"
THERMOSTAT_OPERATING_STATE_PROPERTY = "state"
THERMOSTAT_CURRENT_TEMP_PROPERTY = "Air temperature"
THERMOSTAT_HUMIDITY_PROPERTY = "Humidity"
THERMOSTAT_FAN_MODE_PROPERTY = "mode"
THERMOSTAT_FAN_OFF_PROPERTY = "off"
THERMOSTAT_FAN_STATE_PROPERTY = "state"


class ThermostatMode(IntEnum):
    """Enum with all (known/used) Z-Wave ThermostatModes."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/ThermostatModeCC.ts#L53-L70
    OFF = 0
    HEAT = 1
    COOL = 2
    AUTO = 3
    AUXILIARY = 4
    RESUME_ON = 5
    FAN = 6
    FURNACE = 7
    DRY = 8
    MOIST = 9
    AUTO_CHANGE_OVER = 10
    HEATING_ECON = 11
    COOLING_ECON = 12
    AWAY = 13
    FULL_POWER = 15
    MANUFACTURER_SPECIFIC = 31


class ThermostatOperatingState(IntEnum):
    """Enum with all (known/used) Z-Wave Thermostat OperatingStates."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/ThermostatOperatingStateCC.ts#L38-L51
    IDLE = 0
    HEATING = 1
    COOLING = 2
    FAN_ONLY = 3
    PENDING_HEAT = 4
    PENDING_COOL = 5
    VENT_ECONOMIZER = 6
    AUX_HEATING = 7
    SECOND_STAGE_HEATING = 8
    SECOND_STAGE_COOLING = 9
    SECOND_STAGE_AUX_HEAT = 10
    THIRD_STAGE_AUX_HEAT = 11


class ThermostatSetpointType(IntEnum):
    """Enum with all (known/used) Z-Wave Thermostat Setpoint Types."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/ThermostatSetpointCC.ts#L53-L66
    NA = 0
    HEATING = 1
    COOLING = 2
    FURNACE = 7
    DRY_AIR = 8
    MOIST_AIR = 9
    AUTO_CHANGEOVER = 10
    ENERGY_SAVE_HEATING = 11
    ENERGY_SAVE_COOLING = 12
    AWAY_HEATING = 13
    AWAY_COOLING = 14
    FULL_POWER = 15


THERMOSTAT_MODE_SETPOINT_MAP: dict[int, list[ThermostatSetpointType]] = {
    ThermostatMode.OFF: [],
    ThermostatMode.HEAT: [ThermostatSetpointType.HEATING],
    ThermostatMode.COOL: [ThermostatSetpointType.COOLING],
    ThermostatMode.AUTO: [
        ThermostatSetpointType.HEATING,
        ThermostatSetpointType.COOLING,
    ],
    ThermostatMode.AUXILIARY: [ThermostatSetpointType.HEATING],
    ThermostatMode.FURNACE: [ThermostatSetpointType.FURNACE],
    ThermostatMode.DRY: [ThermostatSetpointType.DRY_AIR],
    ThermostatMode.MOIST: [ThermostatSetpointType.MOIST_AIR],
    ThermostatMode.AUTO_CHANGE_OVER: [ThermostatSetpointType.AUTO_CHANGEOVER],
    ThermostatMode.HEATING_ECON: [ThermostatSetpointType.ENERGY_SAVE_HEATING],
    ThermostatMode.COOLING_ECON: [ThermostatSetpointType.ENERGY_SAVE_COOLING],
    ThermostatMode.AWAY: [
        ThermostatSetpointType.AWAY_HEATING,
        ThermostatSetpointType.AWAY_COOLING,
    ],
    ThermostatMode.FULL_POWER: [ThermostatSetpointType.FULL_POWER],
}
