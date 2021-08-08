"""Command Class specific utility functions for values."""
from ..const import (
    CC_SPECIFIC_METER_TYPE,
    CC_SPECIFIC_SCALE,
    CC_SPECIFIC_SENSOR_TYPE,
    METER_TYPE_TO_SCALE_ENUM_MAP,
    CommandClass,
    MeterScaleType,
    MeterType,
    MultilevelSensorType,
)
from ..exceptions import InvalidCommandClass
from ..model.value import Value


def get_meter_type(value: Value) -> MeterType:
    """Get the MeterType for a given value."""
    if value.command_class != CommandClass.METER:
        raise InvalidCommandClass(value, CommandClass.METER)
    return MeterType(value.metadata.cc_specific[CC_SPECIFIC_METER_TYPE])


def get_meter_scale_type(value: Value) -> MeterScaleType:
    """Get the ScaleType for a given value."""
    meter_type = get_meter_type(value)
    scale_enum = METER_TYPE_TO_SCALE_ENUM_MAP[meter_type]
    return scale_enum(value.metadata.cc_specific[CC_SPECIFIC_SCALE])  # type: ignore


def get_multilevel_sensor_type(value: Value) -> MultilevelSensorType:
    """Get the MultilevelSensorType for a given value."""
    if value.command_class != CommandClass.SENSOR_MULTILEVEL:
        raise InvalidCommandClass(value, CommandClass.SENSOR_MULTILEVEL)
    return MultilevelSensorType(value.metadata.cc_specific[CC_SPECIFIC_SENSOR_TYPE])
