"""Constants for the Energy Production CC."""
from __future__ import annotations

from enum import IntEnum


class EnergyProductionParameter(IntEnum):
    """Energy Production CC parameter."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/cc/src/lib/_Types.ts#L508
    POWER = 0
    TOTAL_PRODUCTION = 1
    TODAYS_PRODUCTION = 2
    TOTAL_TIME = 3


CC_SPECIFIC_PARAMETER = "parameter"
CC_SPECIFIC_SCALE = "scale"


# https://github.com/zwave-js/node-zwave-js/blob/master/packages/cc/src/lib/_Types.ts#L520
class EnergyProductionScaleType(IntEnum):
    """Common base class for Energy Production scale enums."""


class PowerScale(EnergyProductionScaleType):
    """Enum with all known Energy Production power scale values."""

    WATTS = 0


class TotalProductionScale(EnergyProductionScaleType):
    """Enum with all known Energy Production total production scale values."""

    WATT_HOURS = 0


TodaysProductionScale = TotalProductionScale


class TotalTimeScale(EnergyProductionScaleType):
    """Enum with all known Energy Production total time scale values."""

    SECONDS = 0
    HOURS = 1


ENERGY_PRODUCTION_PARAMETER_TO_SCALE_ENUM_MAP: dict[
    EnergyProductionParameter, type[EnergyProductionScaleType]
] = {
    EnergyProductionParameter.POWER: PowerScale,
    EnergyProductionParameter.TOTAL_PRODUCTION: TotalProductionScale,
    EnergyProductionParameter.TODAYS_PRODUCTION: TodaysProductionScale,
    EnergyProductionParameter.TOTAL_TIME: TotalTimeScale,
}
