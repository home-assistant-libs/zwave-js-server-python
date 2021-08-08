"""Command Class specific utility functions for values."""
from typing import Union

from ..const import (
    CC_SPECIFIC_METER_TYPE,
    CC_SPECIFIC_SCALE,
    CC_SPECIFIC_SENSOR_TYPE,
    METER_TYPE_TO_SCALE_ENUM_MAP,
    CommandClass,
    CoolingScale,
    ElectricScale,
    GasScale,
    HeatingScale,
    MeterType,
    MultilevelSensorType,
    WaterScale,
)
from ..exceptions import InvalidCommandClass
from ..model.value import Value


def get_meter_type(value: Value) -> Union[MeterType, None]:
    """Get the MeterType for a given value."""
    if value.command_class != CommandClass.METER:
        raise InvalidCommandClass(value, CommandClass.METER)

    try:
        return MeterType(value.metadata.cc_specific[CC_SPECIFIC_METER_TYPE])
    except ValueError:
        return None


def get_meter_scale_type(
    value: Value,
) -> Union[CoolingScale, ElectricScale, GasScale, HeatingScale, WaterScale, None]:
    """Get the ScaleType for a given value."""
    meter_type = get_meter_type(value)
    if meter_type is None:
        return None
    scale_enum = METER_TYPE_TO_SCALE_ENUM_MAP[meter_type]
    try:
        return scale_enum(value.metadata.cc_specific[CC_SPECIFIC_SCALE])
    except ValueError:
        return None


def get_multilevel_sensor_type(value: Value) -> Union[MultilevelSensorType, None]:
    """Get the MultilevelSensorType for a given value."""
    if value.command_class != CommandClass.SENSOR_MULTILEVEL:
        raise InvalidCommandClass(value, CommandClass.SENSOR_MULTILEVEL)

    try:
        return MultilevelSensorType(value.metadata.cc_specific[CC_SPECIFIC_SENSOR_TYPE])
    except ValueError:
        return None
