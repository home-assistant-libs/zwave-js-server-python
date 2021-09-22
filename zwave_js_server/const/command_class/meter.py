"""Constants for Meter CC."""
from enum import IntEnum
from typing import Dict, Set, Type, Union

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


class ElectricScale(IntEnum):
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


class GasScale(IntEnum):
    """Enum with all known gas meter scale values."""

    CUBIC_METER = 0
    CUBIC_FEET = 1
    PULSE_COUNT = 3


class WaterScale(IntEnum):
    """Enum with all known water meter scale values."""

    CUBIC_METER = 0
    CUBIC_FEET = 1
    US_GALLON = 2
    PULSE_COUNT = 3


class HeatingScale(IntEnum):
    """Enum with all known heating meter scale values."""

    KILOWATT_HOUR = 0


CoolingScale = HeatingScale

MeterScaleType = Union[CoolingScale, ElectricScale, GasScale, HeatingScale, WaterScale]

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
