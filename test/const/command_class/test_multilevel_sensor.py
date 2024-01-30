"""Test the multilevel sensor command class constants."""

from zwave_js_server.const.command_class.multilevel_sensor import (
    UNIT_ABSOLUTE_HUMIDITY,
    UNIT_HERTZ,
    UNIT_KILOGRAM,
    UNIT_MOLE_PER_CUBIC_METER,
    UNIT_PERCENTAGE_VALUE,
)


def test_multilevel_sensor_constants():
    """Test some of the multilevel sensor command class constants.

    Ensure that the enums are not overwriting each other.
    """
    assert len(UNIT_ABSOLUTE_HUMIDITY) == 1
    assert len(UNIT_HERTZ) == 2
    assert len(UNIT_KILOGRAM) == 2
    assert len(UNIT_MOLE_PER_CUBIC_METER) == 7
    assert len(UNIT_PERCENTAGE_VALUE) == 6
