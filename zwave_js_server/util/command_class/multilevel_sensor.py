"""Multilevel Sensor Command Class specific utility functions for values."""
from ...const import CommandClass
from ...const.command_class.multilevel_sensor import (
    CC_SPECIFIC_SCALE,
    CC_SPECIFIC_SENSOR_TYPE,
    MultilevelSensorScaleType,
    MultilevelSensorType,
    MULTILEVEL_SENSOR_TYPE_TO_SCALE_MAP,
)
from ...exceptions import InvalidCommandClass, UnknownValueData
from ...model.value import Value


def get_multilevel_sensor_type(value: Value) -> MultilevelSensorType:
    """Get the MultilevelSensorType for a given value."""
    if value.command_class != CommandClass.SENSOR_MULTILEVEL:
        raise InvalidCommandClass(value, CommandClass.SENSOR_MULTILEVEL)
    try:
        return MultilevelSensorType(value.metadata.cc_specific[CC_SPECIFIC_SENSOR_TYPE])
    except ValueError:
        raise UnknownValueData(  # pylint: disable=raise-missing-from
            value, f"metadata.cc_specific.{CC_SPECIFIC_SENSOR_TYPE}"
        )


def get_multilevel_sensor_scale_type(value: Value) -> MultilevelSensorScaleType:
    """Get the ScaleType for a given value."""
    sensor_type = get_multilevel_sensor_type(value)
    scale_enum = MULTILEVEL_SENSOR_TYPE_TO_SCALE_MAP[sensor_type]
    try:
        return scale_enum(value.metadata.cc_specific[CC_SPECIFIC_SCALE])
    except ValueError:
        raise UnknownValueData(  # pylint: disable=raise-missing-from
            value, f"metadata.cc_specific.{CC_SPECIFIC_SCALE}"
        )
