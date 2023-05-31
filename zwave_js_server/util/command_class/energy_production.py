"""Energy Production Command Class specific utility functions for values."""
from __future__ import annotations

from ...const import CommandClass
from ...const.command_class.energy_production import (
    CC_SPECIFIC_PARAMETER,
    CC_SPECIFIC_SCALE,
    ENERGY_PRODUCTION_PARAMETER_TO_SCALE_ENUM_MAP,
    EnergyProductionParameter,
    EnergyProductionScaleType,
)
from ...exceptions import InvalidCommandClass, UnknownValueData
from ...model.value import Value


def get_energy_production_parameter(value: Value) -> EnergyProductionParameter:
    """Get the EnergyProductionParameter for a given value."""
    if value.command_class != CommandClass.ENERGY_PRODUCTION:
        raise InvalidCommandClass(value, CommandClass.ENERGY_PRODUCTION)
    try:
        return EnergyProductionParameter(
            value.metadata.cc_specific[CC_SPECIFIC_PARAMETER]
        )
    except ValueError:
        raise UnknownValueData(
            value, f"metadata.cc_specific.{CC_SPECIFIC_PARAMETER}"
        ) from None


def get_energy_production_scale_type(value: Value) -> EnergyProductionScaleType:
    """Get the ScaleType for a given value."""
    parameter = get_energy_production_parameter(value)
    scale_enum = ENERGY_PRODUCTION_PARAMETER_TO_SCALE_ENUM_MAP[parameter]
    try:
        return scale_enum(value.metadata.cc_specific[CC_SPECIFIC_SCALE])
    except ValueError:
        raise UnknownValueData(
            value, f"metadata.cc_specific.{CC_SPECIFIC_SCALE}"
        ) from None
