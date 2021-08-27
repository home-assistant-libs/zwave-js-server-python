"""Command Class specific utility functions for values."""
from ..const import CommandClass
from ..const.command_class.meter import (
    CC_SPECIFIC_METER_TYPE,
    CC_SPECIFIC_SCALE,
    METER_TYPE_TO_SCALE_ENUM_MAP,
    MeterScaleType,
    MeterType,
)
from ..const.command_class.multilevel_sensor import (
    CC_SPECIFIC_SENSOR_TYPE,
    MultilevelSensorType,
)
from ..exceptions import InvalidCommandClass, UnknownValueData
from ..model.value import Value


def get_meter_type(value: Value) -> MeterType:
    """Get the MeterType for a given value."""
    if value.command_class != CommandClass.METER:
        raise InvalidCommandClass(value, CommandClass.METER)
    try:
        return MeterType(value.metadata.cc_specific[CC_SPECIFIC_METER_TYPE])
    except ValueError:
        raise UnknownValueData(  # pylint: disable=raise-missing-from
            value, f"metadata.cc_specific.{CC_SPECIFIC_METER_TYPE}"
        )


def get_meter_scale_type(value: Value) -> MeterScaleType:
    """Get the ScaleType for a given value."""
    meter_type = get_meter_type(value)
    scale_enum = METER_TYPE_TO_SCALE_ENUM_MAP[meter_type]
    try:
        return scale_enum(value.metadata.cc_specific[CC_SPECIFIC_SCALE])
    except ValueError:
        raise UnknownValueData(  # pylint: disable=raise-missing-from
            value, f"metadata.cc_specific.{CC_SPECIFIC_SCALE}"
        )


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
