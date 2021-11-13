"""Script to generate Multilevel Sensor CC constants."""
from __future__ import annotations

from collections import defaultdict
import json
import os
import re
import subprocess
from typing import Callable, List

import requests
from slugify import slugify

GITHUB_PROJECT = "zwave-js/node-zwave-js"
BRANCH_NAME = "master"
SENSOR_TYPES_FILE_PATH = "packages/config/config/sensorTypes.json"
DEFAULT_SCALES_FILE_PATH = "packages/config/config/scales.json"

base_path = os.path.dirname(__file__)


MULTILEVEL_SENSOR_CONST_FILE_PATH = os.path.join(
    base_path, "../zwave_js_server/const/command_class/multilevel_sensor.py"
)


def remove_comments(text: str) -> str:
    """Remove comments from a JSON string."""
    return "\n".join(
        line for line in text.split("\n") if not line.strip().startswith("//")
    )


def remove_paranthesis(text: str) -> str:
    """Remove text in paranethesis from a string."""
    return re.sub(r"\([^)]*\)", "", text)


def enum_name_format(name: str, should_remove_paranthesis: bool) -> str:
    """Convert sensor/scale name to enum format."""
    if should_remove_paranthesis:
        name = remove_paranthesis(name)
    return slugify(name, separator="_").upper()


def normalize_name(name: str) -> str:
    """Convert a sensor/scale name into a normalized name."""
    return enum_name_format(name, True).replace("_", " ").title()


def format_for_class_name(name: str) -> str:
    """Convert sensor/scale name to class name format."""
    return f"{normalize_name(name).replace(' ', '')}Scale"


def normalize_scale_definition(scale_definitions: dict[str, dict]) -> dict[str, int]:
    """Convert a scales definition dictionary into a normalized dictionary."""
    scale_def_ = {}
    for scale_id, scale_props in scale_definitions.items():
        scale_id = int(scale_id, 16)
        scale_name_ = enum_name_format(scale_props["label"], True)
        scale_def_[scale_name_] = scale_id

    return scale_def_


sensor_types = json.loads(
    remove_comments(
        requests.get(
            (
                f"https://raw.githubusercontent.com/{GITHUB_PROJECT}/{BRANCH_NAME}/"
                f"{SENSOR_TYPES_FILE_PATH}"
            )
        ).text
    )
)
default_scales = json.loads(
    remove_comments(
        requests.get(
            (
                f"https://raw.githubusercontent.com/{GITHUB_PROJECT}/{BRANCH_NAME}/"
                f"{DEFAULT_SCALES_FILE_PATH}"
            )
        ).text
    )
)

scales = {
    normalize_name(scale_name): normalize_scale_definition(scale_def)
    for scale_name, scale_def in default_scales.items()
}

sensors = {}
for sensor_id, sensor_props in sensor_types.items():
    sensor_id = int(sensor_id, 16)
    scale_def = sensor_props["scales"]
    remove_paranthesis_: bool = True
    if sensor_id in (87, 88):
        remove_paranthesis_: bool = False
    sensor_name = enum_name_format(sensor_props["label"], remove_paranthesis_)
    sensors[sensor_name] = {"id": sensor_id}
    if isinstance(scale_def, str):
        sensors[sensor_name]["scale"] = normalize_name(
            scale_def.replace("$SCALES:", "")
        )
    else:
        scales[sensor_name] = normalize_scale_definition(scale_def)
        sensors[sensor_name]["scale"] = normalize_name(sensor_name)


def generate_int_enum_class_definition(
    class_name: str,
    enum_dict: dict[str, str | dict],
    enum_ref_url: str | None = None,
    get_id_func: Callable | None = None,
    docstring_info: str = "",
) -> List[str]:
    """Generate an IntEnum class definition as an array of lines of string."""
    class_def = []
    class_def.append(f"class {class_name}(IntEnum):")
    docstring = (
        f'"""Enum for known {docstring_info} multilevel sensor types."""'.replace(
            "  ", " "
        )
    )
    class_def.append(f"    {docstring}")
    if enum_ref_url:
        class_def.append(f"    # {enum_ref_url}")
    for enum_name, enum_id in enum_dict.items():
        if get_id_func:
            enum_id = get_id_func(enum_id)
        class_def.append(f"    {enum_name} = {enum_id}")
    return class_def


SENSOR_TYPE_URL = (
    f"https://github.com/{GITHUB_PROJECT}/blob/{BRANCH_NAME}/{SENSOR_TYPES_FILE_PATH}"
)

lines = [
    '"""Constants for the Multilevel Sensor CC."""',
    "",
    "# ----------------------------------------------------------------------------------- #",
    "# **BEGINNING OF AUTOGENERATED CONTENT** (TO ADD ADDITIONAL MANUAL CONTENT, LOOK FOR  #",
    '# THE "END OF AUTOGENERATED CONTENT" COMMENT BLOCK AND ADD YOUR CODE BELOW IT)        #',
    "# ----------------------------------------------------------------------------------- #",
    "",
    "from enum import IntEnum",
    "from typing import Dict, Type, Union",
    'CC_SPECIFIC_SCALE = "scale"',
    'CC_SPECIFIC_SENSOR_TYPE = "sensorType"',
]

lines.extend(
    generate_int_enum_class_definition(
        "MultilevelSensorType",
        sensors,
        SENSOR_TYPE_URL,
        get_id_func=lambda x: x["id"],
    )
)

unit_name_to_enum_map = defaultdict(list)
for scale_name, scale_dict in scales.items():
    lines.extend(
        generate_int_enum_class_definition(
            format_for_class_name(scale_name),
            scale_dict,
            SENSOR_TYPE_URL,
            docstring_info=f"scales for {scale_name}",
        )
    )
    for unit_name in scale_dict.keys():
        unit_name_to_enum_map[unit_name].append(
            f"{format_for_class_name(scale_name)}.{unit_name}"
        )

scale_class_names = [format_for_class_name(scale_name) for scale_name in scales]
lines.extend(
    [f"MultilevelSensorScaleType = Union[{', '.join(sorted(scale_class_names))}]", ""]
)

multilevel_sensor_type_to_scale_map_line: str = (
    "MULTILEVEL_SENSOR_TYPE_TO_SCALE_MAP: Dict[MultilevelSensorType, "
    "Type[MultilevelSensorScaleType]] = {"
)
for sensor_name, sensor_def in sensors.items():
    multilevel_sensor_type_to_scale_map_line += (
        f"    MultilevelSensorType.{sensor_name}: "
        f"{format_for_class_name(sensor_def['scale'])},"
    )
multilevel_sensor_type_to_scale_map_line += "}"
lines.append(multilevel_sensor_type_to_scale_map_line)
lines.append("")

for unit_name, unit_enums in unit_name_to_enum_map.items():
    lines.append(f"UNIT_{unit_name} = {{{','.join(sorted(unit_enums))}}}")

lines.extend(
    [
        "",
        "# ----------------------------------------------------------------------------------- #",
        "# **END OF AUTOGENERATED CONTENT** (DO NOT EDIT/REMOVE THIS COMMENT BLOCK AND DO NOT  #",
        "# EDIT ANYTHING ABOVE IT. IF A NEW IMPORT IS NEEDED, UPDATE THE LINES AROUND 135      #",
        "# IN scripts/generate_multilevel_sensor_constants.py THEN RE-RUN THE SCRIPT. ALL      #",
        "# LINES WRITTEN BELOW THIS BLOCK WILL BE PRESERVED AS LONG AS THIS BLOCK REMAINS)     #",
        "# ----------------------------------------------------------------------------------- #",
        "",
    ]
)

with open(MULTILEVEL_SENSOR_CONST_FILE_PATH, "r", encoding="utf-8") as fp:
    existing_const_file = fp.readlines()

manually_written_code_start_idx = (
    next(
        i
        for i, line in enumerate(existing_const_file)
        if "**END OF AUTOGENERATED CONTENT**" in line
    )
    + 6
)
if len(existing_const_file) > manually_written_code_start_idx:
    lines.extend(
        [
            line.strip("\n")
            for line in existing_const_file[manually_written_code_start_idx:]
        ]
    )

with open(MULTILEVEL_SENSOR_CONST_FILE_PATH, "w", encoding="utf-8") as fp:
    fp.write("\n".join(lines))

if subprocess.run(["which", "black"], capture_output=True, check=True).stdout:
    subprocess.run(
        ["black", MULTILEVEL_SENSOR_CONST_FILE_PATH],
        check=True,
    )
else:
    print("Could not run black on new file, please run it to properly format it.")
