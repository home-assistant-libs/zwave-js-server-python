"""Script to generate Multilevel Sensor CC constants."""
from __future__ import annotations

import json
import re
from typing import Callable

import requests
from slugify import slugify

GITHUB_PROJECT = "zwave-js/node-zwave-js"
BRANCH_NAME = "master"
SENSOR_TYPES_FILE_PATH = "packages/config/config/sensorTypes.json"
DEFAULT_SCALES_FILE_PATH = "packages/config/config/scales.json"


def remove_comments(text: str) -> str:
    """Remove comments from a JSON string."""
    lines = text.split("\n")

    return "\n".join(line for line in lines if not line.strip().startswith("//"))


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
    return normalize_name(name).replace(" ", "")


def normalize_scale_definition(scale_definitions: dict[str, dict]) -> dict[str, int]:
    """Convert a scales definition dictionary into a normalized dictionary."""
    scale_def = {}
    for scale_id, scale_props in scale_definitions.items():
        scale_id = int(scale_id, 16)
        scale_name = enum_name_format(scale_props["label"], True)
        scale_def[scale_name] = scale_id

    return scale_def


sensor_types = json.loads(
    remove_comments(
        requests.get(
            f"https://raw.githubusercontent.com/{GITHUB_PROJECT}/{BRANCH_NAME}/{SENSOR_TYPES_FILE_PATH}"
        ).text
    )
)
default_scales = json.loads(
    remove_comments(
        requests.get(
            f"https://raw.githubusercontent.com/{GITHUB_PROJECT}/{BRANCH_NAME}/{DEFAULT_SCALES_FILE_PATH}"
        ).text
    )
)

scales = {}
for scale_name, scale_def in default_scales.items():
    scales[normalize_name(scale_name)] = normalize_scale_definition(scale_def)

sensors = {}
for sensor_id, sensor_props in sensor_types.items():
    sensor_id = int(sensor_id, 16)
    scale_def = sensor_props["scales"]
    remove_paranthesis_ = True
    if sensor_id in (87, 88):
        remove_paranthesis_ = False
    sensor_name = enum_name_format(sensor_props["label"], remove_paranthesis_)
    sensors[sensor_name] = {"id": sensor_id}
    if isinstance(scale_def, str):
        sensors[sensor_name]["scale"] = normalize_name(
            scale_def.replace("$SCALES:", "")
        )
    else:
        scales[sensor_name] = normalize_scale_definition(scale_def)
        sensors[sensor_name]["scale"] = normalize_name(sensor_name)


def generate_intenum_class_definition(
    class_name: str,
    enum_dict: dict[str, str | dict],
    enum_ref_url: str | None = None,
    get_id_func: Callable | None = None,
    docstring_info: str = "",
) -> str:
    """Print an IntEnum class."""
    class_def = []
    class_def.append(f"class {class_name}(IntEnum):")
    class_def.append(
        f'    """Enum with all known {docstring_info} multilevel sensor types."""'.replace(
            "  ", " "
        )
    )
    class_def.append("")
    if enum_ref_url:
        class_def.append(f"    # {enum_ref_url}")
        for enum_name, enum_id in enum_dict.items():
            if get_id_func:
                enum_id = get_id_func(enum_id)
            class_def.append(f"    {enum_name} = {enum_id}")
    class_def.append("")
    class_def.append("")
    return "\n".join(class_def)


SENSOR_TYPE_URL = (
    f"https://github.com/{GITHUB_PROJECT}/blob/{BRANCH_NAME}/{SENSOR_TYPES_FILE_PATH}"
)

print(
    generate_intenum_class_definition(
        "MultilevelSensorType",
        sensors,
        SENSOR_TYPE_URL,
        get_id_func=lambda x: x["id"],
    )
)

for scale_name, scale_dict in scales.items():
    print(
        generate_intenum_class_definition(
            f"{format_for_class_name(scale_name)}Scale",
            scale_dict,
            SENSOR_TYPE_URL,
            docstring_info=f"scales for {scale_name}",
        )
    )

print("MULTILEVEL_SENSOR_TYPE_TO_SCALE_MAP = {")
for sensor_name, sensor_def in sensors.items():
    print(
        f"    MultilevelSensorType.{sensor_name}: {format_for_class_name(sensor_def['scale'])}Scale,"
    )
print("}")
print()
print()

scale_class_names = [
    f"{format_for_class_name(scale_name)}Scale" for scale_name in scales
]
print(f"MultilevelSensorScaleType = Union[{', '.join(sorted(scale_class_names))}]")
print()
print()
