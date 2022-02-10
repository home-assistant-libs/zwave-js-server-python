"""Test command class utility functions."""
import pytest

from zwave_js_server.const import CommandClass
from zwave_js_server.const.command_class.multilevel_sensor import (
    MultilevelSensorType,
    TemperatureScale,
)
from zwave_js_server.exceptions import ValueHasInvalidCommandClass, UnknownValueData
from zwave_js_server.model.node import Node
from zwave_js_server.model.value import MetaDataType, Value, ValueDataType, get_value_id
from zwave_js_server.util.command_class.multilevel_sensor import (
    CC_SPECIFIC_SCALE,
    CC_SPECIFIC_SENSOR_TYPE,
    get_multilevel_sensor_scale_type,
    get_multilevel_sensor_type,
)


async def test_get_multilevel_sensor_type(multisensor_6: Node):
    """Test get_multilevel_sensor_type function."""
    node = multisensor_6

    value_id = get_value_id(node, CommandClass.SENSOR_BINARY, "Any")
    with pytest.raises(ValueHasInvalidCommandClass):
        get_multilevel_sensor_type(node.values.get(value_id))

    value_id = get_value_id(node, CommandClass.SENSOR_MULTILEVEL, "Air temperature")
    assert (
        get_multilevel_sensor_type(node.values.get(value_id))
        == MultilevelSensorType.AIR_TEMPERATURE
    )


async def test_get_invalid_multilevel_sensor_type(invalid_multilevel_sensor_type: Node):
    """Test receiving an invalid multilevel sensor type."""
    node = invalid_multilevel_sensor_type

    value_id = get_value_id(
        node, CommandClass.SENSOR_MULTILEVEL, "UNKNOWN (0x00)", endpoint=2
    )
    with pytest.raises(UnknownValueData):
        get_multilevel_sensor_type(node.values.get(value_id))


async def test_get_multilevel_sensor_scale_type(multisensor_6: Node):
    """Test get_multilevel_sensor_scale_type function."""
    node = multisensor_6

    value_id = get_value_id(node, CommandClass.SENSOR_MULTILEVEL, "Air temperature")
    assert (
        get_multilevel_sensor_scale_type(node.values.get(value_id))
        == TemperatureScale.CELSIUS
    )


async def test_get_invalid_multilevel_sensor_scale_type(
    invalid_multilevel_sensor_type: Node,
):
    """Test receiving an invalid multilevel sensor scale type."""
    node = invalid_multilevel_sensor_type

    # Create value with an invalid scale ID
    metadata = MetaDataType(
        ccSpecific={CC_SPECIFIC_SENSOR_TYPE: 1, CC_SPECIFIC_SCALE: -1}
    )
    value_data = ValueDataType(
        commandClass=CommandClass.SENSOR_MULTILEVEL,
        commandClassName="Multilevel Sensor",
        endpoint=0,
        property="value",
        propertyKey=9999999,
        metadata=metadata,
    )
    value = Value(node, value_data)
    with pytest.raises(UnknownValueData):
        get_multilevel_sensor_scale_type(value)
