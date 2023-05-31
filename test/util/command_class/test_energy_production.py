"""Test Energy Production command class utility functions."""
import pytest

from zwave_js_server.const import CommandClass
from zwave_js_server.const.command_class.energy_production import (
    CC_SPECIFIC_PARAMETER,
    CC_SPECIFIC_SCALE,
    EnergyProductionParameter,
    PowerScale,
)
from zwave_js_server.exceptions import InvalidCommandClass, UnknownValueData
from zwave_js_server.model.node import Node
from zwave_js_server.model.value import (
    MetaDataType,
    Value,
    ValueDataType,
    get_value_id_str,
)
from zwave_js_server.util.command_class.energy_production import (
    get_energy_production_parameter,
    get_energy_production_scale_type,
)


async def test_get_energy_production_parameter(energy_production: Node):
    """Test get_energy_production_parameter function."""
    node = energy_production

    value_id = get_value_id_str(node, CommandClass.VERSION, "protocolVersion")
    with pytest.raises(InvalidCommandClass):
        get_energy_production_parameter(node.values.get(value_id))

    value_id = get_value_id_str(
        node, CommandClass.ENERGY_PRODUCTION, "value", property_key=0
    )
    assert (
        get_energy_production_parameter(node.values.get(value_id))
        == EnergyProductionParameter.POWER
    )


async def test_invalid_get_energy_production_parameter(
    invalid_multilevel_sensor_type: Node,
):
    """Test receiving an invalid energy production parameter."""
    node = invalid_multilevel_sensor_type

    # Create value with an invalid parameter ID
    metadata = MetaDataType(ccSpecific={CC_SPECIFIC_PARAMETER: -1})
    value_data = ValueDataType(
        commandClass=CommandClass.ENERGY_PRODUCTION,
        commandClassName="EnergyProduction",
        endpoint=0,
        property="value",
        propertyKey=0,
        metadata=metadata,
    )
    value = Value(node, value_data)
    with pytest.raises(UnknownValueData):
        get_energy_production_parameter(value)


async def test_get_energy_production_scale_type(energy_production: Node):
    """Test get_energy_production_scale_type function."""
    node = energy_production

    value_id = get_value_id_str(
        node, CommandClass.ENERGY_PRODUCTION, "value", property_key=0
    )
    assert (
        get_energy_production_scale_type(node.values.get(value_id)) == PowerScale.WATTS
    )


async def test_invalid_get_energy_production_scale_type(
    invalid_multilevel_sensor_type: Node,
):
    """Test receiving an invalid energy production scale type."""
    node = invalid_multilevel_sensor_type

    # Create value with an invalid scale ID
    metadata = MetaDataType(
        ccSpecific={CC_SPECIFIC_PARAMETER: 0, CC_SPECIFIC_SCALE: -1}
    )
    value_data = ValueDataType(
        commandClass=CommandClass.ENERGY_PRODUCTION,
        commandClassName="EnergyProduction",
        endpoint=0,
        property="value",
        propertyKey=0,
        metadata=metadata,
    )
    value = Value(node, value_data)
    with pytest.raises(UnknownValueData):
        get_energy_production_scale_type(value)
