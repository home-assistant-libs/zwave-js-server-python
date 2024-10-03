#!/usr/bin/env python3
"""Script to generate Multilevel Sensor CC constants."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Mapping
import json
import os
import pathlib

from const import AUTO_GEN_POST, AUTO_GEN_PRE
from helpers import (
    enum_name_format,
    format_for_class_name,
    get_manually_written_code,
    get_registry_location,
    run_black,
    split_camel_case,
)

SENSORS_FILE_PATH = "sensors.json"

CONST_FILE_PATH = (
    pathlib.Path(__file__).parent.parent
    / "zwave_js_server/const/command_class/multilevel_sensor.py"
)


def normalize_scale_definition(scale_definitions: dict[str, dict]) -> dict[str, int]:
    """Convert a scales definition dictionary into a normalized dictionary."""
    scale_def_ = {}
    for scale_id, scale_props in scale_definitions.items():
        _scale_id = int(scale_id, 16)
        scale_name_ = enum_name_format(scale_props["label"], True)
        scale_def_[scale_name_] = _scale_id

    return dict(sorted(scale_def_.items(), key=lambda kv: kv[0]))


if not os.path.exists(SENSORS_FILE_PATH):
    raise FileNotFoundError(f"{SENSORS_FILE_PATH} not found")

with open(SENSORS_FILE_PATH) as fp:
    sensors_file = json.load(fp)

scales = {}
sensors = {}

for sensor_props in sensors_file:
    sensor_id = sensor_props["key"]
    scale_def = sensor_props["scales"]
    remove_parenthesis_ = True
    if sensor_id in (87, 88):
        remove_parenthesis_ = False
    sensor_name = enum_name_format(sensor_props["label"], remove_parenthesis_)
    sensors[sensor_name] = {"id": sensor_id, "label": sensor_props["label"]}
    if not (scale_name := split_camel_case(sensor_props.get("scaleGroupName", ""))):
        scale_name = sensor_name
    scales[scale_name] = normalize_scale_definition(scale_def)
    sensors[sensor_name]["scale"] = scale_name

scales = dict(sorted(scales.items(), key=lambda kv: kv[0]))
sensors = dict(sorted(sensors.items(), key=lambda kv: kv[0]))


def generate_int_enum_class_definition(
    class_name: str,
    enum_map: Mapping[str, int | str | dict],
    enum_ref_url: str | None = None,
    get_id_func: Callable | None = None,
    docstring_info: str = "",
    base_class: str = "IntEnum",
) -> list[str]:
    """Generate an IntEnum class definition as an array of lines of string."""
    class_def: list[str] = []
    class_def.append(f"class {class_name}({base_class}):")
    docstring = (
        f'"""Enum for known {docstring_info} multilevel sensor types."""'.replace(
            "  ", " "
        )
    )
    class_def.append(f"    {docstring}")
    if enum_ref_url:
        class_def.append(f"    # {enum_ref_url}")
    for enum_name, enum_id in enum_map.items():
        if get_id_func:
            enum_id = get_id_func(enum_id)
        class_def.append(f"    {enum_name} = {enum_id}")
    return class_def


def generate_int_enum_base_class(class_name: str, docstring: str) -> list[str]:
    """Generate an IntEnum base class definition."""
    class_def: list[str] = []
    class_def.append(f"class {class_name}(IntEnum):")
    class_def.append(f"\t{docstring}")
    return class_def


SENSOR_TYPE_URL = get_registry_location("SensorTypes.ts")

lines = [
    '"""Constants for the Multilevel Sensor CC."""',
    *AUTO_GEN_PRE,
    "from __future__ import annotations",
    "",
    "from enum import IntEnum",
    'CC_SPECIFIC_SCALE = "scale"',
    'CC_SPECIFIC_SENSOR_TYPE = "sensorType"',
    "",
]

lines.extend(
    [f"{sensor}_PROPERTY = \"{data['label']}\"" for sensor, data in sensors.items()]
)

lines.extend(
    generate_int_enum_class_definition(
        "MultilevelSensorType",
        sensors,
        SENSOR_TYPE_URL,
        get_id_func=lambda x: x["id"],
    )
)

lines.extend(
    generate_int_enum_base_class(
        "MultilevelSensorScaleType",
        docstring='"""Common base class for multilevel sensor scale enums."""',
    )
)

_unit_name_to_enum_map = defaultdict(list)
for scale_name, scale_dict in scales.items():
    lines.extend(
        generate_int_enum_class_definition(
            format_for_class_name(scale_name, "Scale"),
            scale_dict,
            SENSOR_TYPE_URL,
            docstring_info=f"scales for {scale_name}",
            base_class="MultilevelSensorScaleType",
        )
    )
    for unit_name in scale_dict.keys():
        _unit_name_to_enum_map[unit_name].append(
            f"{format_for_class_name(scale_name, 'Scale')}.{unit_name}"
        )
unit_name_to_enum_map = dict(
    sorted(_unit_name_to_enum_map.items(), key=lambda kv: kv[0])
)
for unit_name, enum_list in unit_name_to_enum_map.items():
    unit_name_to_enum_map[unit_name] = sorted(enum_list)


multilevel_sensor_type_to_scale_map_line = (
    "MULTILEVEL_SENSOR_TYPE_TO_SCALE_MAP: dict[MultilevelSensorType, "
    "type[MultilevelSensorScaleType]] = {"
)
for sensor_name, sensor_def in sensors.items():
    multilevel_sensor_type_to_scale_map_line += (
        f"    MultilevelSensorType.{sensor_name}: "
        f"{format_for_class_name(sensor_def['scale'], 'Scale')},"
    )
multilevel_sensor_type_to_scale_map_line += "}"
lines.append(multilevel_sensor_type_to_scale_map_line)
lines.append("")

for unit_name, unit_enums in unit_name_to_enum_map.items():
    lines.append(
        f"UNIT_{unit_name}: list[MultilevelSensorScaleType] = [{','.join(sorted(unit_enums))}]"
    )

lines.extend(AUTO_GEN_POST)
lines.extend(get_manually_written_code(CONST_FILE_PATH))
CONST_FILE_PATH.write_text("\n".join(lines), encoding="utf-8")

run_black(CONST_FILE_PATH)
