"""Constants for Meter CC."""
from enum import IntEnum
from typing import Dict, Set, Type

VALUE_PROPERTY = "value"

CC_SPECIFIC_SCALE = "scale"
CC_SPECIFIC_METER_TYPE = "meterType"
CC_SPECIFIC_RATE_TYPE = "rateType"

RESET_METER_CC_API = "reset"

# optional attributes when calling the Meter CC reset API.
# https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/MeterCC.ts#L873-L881
RESET_METER_OPTION_TARGET_VALUE = "targetValue"
RESET_METER_OPTION_TYPE = "type"


# https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/meters.json
class MeterType(IntEnum):
    """Enum with all known meter types."""

    ELECTRIC = 1
    GAS = 2
    WATER = 3
    HEATING = 4
    COOLING = 5


class MeterScaleType(IntEnum):
    """Common base class for meter scale enums."""


class ElectricScale(MeterScaleType):
    """Enum with all known electric meter scale values."""

    KILOWATT_HOUR = 0
    KILOVOLT_AMPERE_HOUR = 1
    WATT = 2
    PULSE_COUNT = 3
    VOLT = 4
    AMPERE = 5
    POWER_FACTOR = 6
    KILOVOLT_AMPERE_REACTIVE = 7
    KILOVOLT_AMPERE_REACTIVE_HOUR = 8


class GasScale(MeterScaleType):
    """Enum with all known gas meter scale values."""

    CUBIC_METER = 0
    CUBIC_FEET = 1
    PULSE_COUNT = 3


class WaterScale(MeterScaleType):
    """Enum with all known water meter scale values."""

    CUBIC_METER = 0
    CUBIC_FEET = 1
    US_GALLON = 2
    PULSE_COUNT = 3


class HeatingScale(MeterScaleType):
    """Enum with all known heating meter scale values."""

    KILOWATT_HOUR = 0


CoolingScale = HeatingScale

METER_TYPE_TO_SCALE_ENUM_MAP: Dict[MeterType, Type[MeterScaleType]] = {
    MeterType.ELECTRIC: ElectricScale,
    MeterType.GAS: GasScale,
    MeterType.WATER: WaterScale,
    MeterType.HEATING: HeatingScale,
    MeterType.COOLING: CoolingScale,
}

ENERGY_TOTAL_INCREASING_METER_TYPES: Set[MeterScaleType] = {
    ElectricScale.KILOWATT_HOUR,
    ElectricScale.KILOVOLT_AMPERE_HOUR,
    ElectricScale.KILOVOLT_AMPERE_REACTIVE_HOUR,
    HeatingScale.KILOWATT_HOUR,
    CoolingScale.KILOWATT_HOUR,
    ElectricScale.PULSE_COUNT,
}
POWER_METER_TYPES: Set[MeterScaleType] = {
    ElectricScale.WATT,
    ElectricScale.KILOVOLT_AMPERE_REACTIVE,
}
POWER_FACTOR_METER_TYPES: Set[MeterScaleType] = {ElectricScale.POWER_FACTOR}
VOLTAGE_METER_TYPES: Set[MeterScaleType] = {ElectricScale.VOLT}
CURRENT_METER_TYPES: Set[MeterScaleType] = {ElectricScale.AMPERE}
GAS_METER_TYPES: Set[MeterScaleType] = {
    GasScale.CUBIC_METER,
    GasScale.CUBIC_FEET,
    GasScale.PULSE_COUNT,
}
WATER_METER_TYPES: Set[MeterScaleType] = {
    WaterScale.CUBIC_METER,
    WaterScale.CUBIC_FEET,
    WaterScale.US_GALLON,
    WaterScale.PULSE_COUNT,
}

UNIT_KILOWATT_HOUR: Set[MeterScaleType] = {
    ElectricScale.KILOWATT_HOUR,
    HeatingScale.KILOWATT_HOUR,
    CoolingScale.KILOWATT_HOUR,
}
UNIT_KILOVOLT_AMPERE_HOUR: Set[MeterScaleType] = {ElectricScale.KILOVOLT_AMPERE_HOUR}
UNIT_WATT: Set[MeterScaleType] = {ElectricScale.WATT}
UNIT_PULSE_COUNT: Set[MeterScaleType] = {
    ElectricScale.PULSE_COUNT,
    GasScale.PULSE_COUNT,
    WaterScale.PULSE_COUNT,
}
UNIT_VOLT: Set[MeterScaleType] = {ElectricScale.VOLT}
UNIT_AMPERE: Set[MeterScaleType] = {ElectricScale.AMPERE}
UNIT_POWER_FACTOR: Set[MeterScaleType] = {ElectricScale.POWER_FACTOR}
UNIT_KILOVOLT_AMPERE_REACTIVE: Set[MeterScaleType] = {
    ElectricScale.KILOVOLT_AMPERE_REACTIVE
}
UNIT_KILOVOLT_AMPERE_REACTIVE_HOUR: Set[MeterScaleType] = {
    ElectricScale.KILOVOLT_AMPERE_REACTIVE_HOUR
}
UNIT_CUBIC_METER: Set[MeterScaleType] = {GasScale.CUBIC_METER, WaterScale.CUBIC_METER}
UNIT_CUBIC_FEET: Set[MeterScaleType] = {GasScale.CUBIC_FEET, WaterScale.CUBIC_FEET}
UNIT_US_GALLON: Set[MeterScaleType] = {WaterScale.US_GALLON}
