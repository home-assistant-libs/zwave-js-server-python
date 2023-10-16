#!/usr/bin/env python3
"""Script to generate Notification CC constants."""
from __future__ import annotations

from collections.abc import Callable, Mapping
import json
import pathlib
import re
import subprocess
import sys

import requests
from slugify import slugify

GITHUB_PROJECT = "zwave-js/node-zwave-js"
BRANCH_NAME = "master"
NOTIFICATIONS_FILE_PATH = "packages/config/config/notifications.json"

CONST_FILE_PATH = (
    pathlib.Path(__file__).parent.parent
    / "zwave_js_server/const/command_class/notification.py"
)


def remove_comments(text: str) -> str:
    """Remove comments from a JSON string."""
    return "\n".join(
        line for line in text.split("\n") if not line.strip().startswith("//")
    )


def remove_parenthesis(text: str) -> str:
    """Remove text in parenthesis from a string."""
    return re.sub(r"\([^)]*\)", "", text)


def enum_name_format(name: str, should_remove_parenthesis: bool) -> str:
    """Convert sensor/scale name to enum format."""
    if should_remove_parenthesis:
        name = remove_parenthesis(name)
    return slugify(name, separator="_").upper()


def normalize_name(name: str) -> str:
    """Convert a sensor/scale name into a normalized name."""
    return enum_name_format(name, True).replace("_", " ").title()


def format_for_class_name(name: str) -> str:
    """Convert sensor/scale name to class name format."""
    return normalize_name(name).replace(" ", "")


notifications_file = json.loads(
    remove_comments(
        requests.get(
            (
                f"https://raw.githubusercontent.com/{GITHUB_PROJECT}/{BRANCH_NAME}/"
                f"{NOTIFICATIONS_FILE_PATH}"
            ),
            timeout=10,
        ).text
    )
)

notifications = {}
params = {}
for notification_type, notification_payload in notifications_file.items():
    notification_type = int(notification_type, 16)
    notification_name = notification_payload["name"].title()
    notifications[notification_name] = {
        "type": notification_type,
        "events": {},
    }
    for event in notification_payload.get("variables", []):
        event_name = event["name"].title()
        states = notifications[notification_name]["events"]
        for state_id, state_props in event["states"].items():
            state_id = int(state_id, 16)
            state_name = state_props["label"].title()
            if (
                state_name.lower() not in event_name.lower()
                and event_name.lower() not in state_name.lower()
            ):
                state_name = f"{event_name} {state_name}"
            states[state_name] = state_id
            if "params" in state_props and state_props["params"]["type"] == "enum":
                for enum_id, enum_name in state_props["params"]["values"].items():
                    enum_id = int(enum_id, 16)
                    params.setdefault(notification_name, {}).setdefault(state_name, {})[
                        enum_name.title()
                    ] = enum_id
    for event_id, event_data in notification_payload.get("events", {}).items():
        event_id = int(event_id, 16)
        notifications[notification_name]["events"][
            event_data["label"].title()
        ] = event_id


notifications = dict(sorted(notifications.items(), key=lambda kv: kv[0]))
params = dict(sorted(params.items(), key=lambda kv: kv[0]))
for notification_name, enum_data in params.items():
    params[notification_name] = dict(sorted(enum_data.items(), key=lambda kv: kv[0]))


def generate_int_enum_class_definition(
    class_name: str,
    enum_map: Mapping[str, int | str | dict],
    enum_ref_url: str | None = None,
    get_id_func: Callable | None = None,
    docstring_info: str = "",
    base_class: str = "IntEnum",
    include_missing: bool = False,
) -> list[str]:
    """Generate an IntEnum class definition as an array of lines of string."""
    class_def: list[str] = []
    class_def.append(f"class {class_name}({base_class}):")
    docstring = f'"""Enum for known {docstring_info}."""'.replace("  ", " ")
    class_def.append(f"    {docstring}")
    if enum_ref_url:
        class_def.append(f"    # {enum_ref_url}")
    if include_missing:
        class_def.append("    UNKNOWN = -1")
    for _enum_name, _enum_id in sorted(enum_map.items(), key=lambda x: x[0]):
        if get_id_func:
            _enum_id = get_id_func(_enum_id)
        class_def.append(f"    {enum_name_format(_enum_name, False)} = {_enum_id}")
    if include_missing:
        class_def.extend(
            [
                "    @classmethod",
                f"    def _missing_(cls: type, value: object) -> {class_name}:  # noqa: ARG003",
                '        """Set default enum member if an unknown value is provided."""',
                f"        return {class_name}.UNKNOWN",
            ]
        )
    return class_def


def generate_int_enum_base_class(class_name: str, docstring: str) -> list[str]:
    """Generate an IntEnum base class definition."""
    class_def: list[str] = []
    class_def.append(f"class {class_name}(IntEnum):")
    class_def.append(f"    {docstring}")
    return class_def


NOTIFICATIONS_URL = (
    f"https://github.com/{GITHUB_PROJECT}/blob/{BRANCH_NAME}/{NOTIFICATIONS_FILE_PATH}"
)

lines = [
    "# pylint: disable=line-too-long",
    '"""Constants for the Notification CC."""',
    "",
    "# ----------------------------------------------------------------------------------- #",
    "# **BEGINNING OF AUTOGENERATED CONTENT** (TO ADD ADDITIONAL MANUAL CONTENT, LOOK FOR  #",
    '# THE "END OF AUTOGENERATED CONTENT" COMMENT BLOCK AND ADD YOUR CODE BELOW IT)        #',
    "# ----------------------------------------------------------------------------------- #",
    "",
    "from __future__ import annotations",
    "",
    "from enum import IntEnum",
    'CC_SPECIFIC_NOTIFICATION_TYPE = "notificationType"',
]

lines.extend(
    generate_int_enum_class_definition(
        "NotificationType",
        notifications,
        NOTIFICATIONS_URL,
        get_id_func=lambda x: x["type"],
        docstring_info="notification types",
    )
)

lines.extend(
    generate_int_enum_base_class(
        "NotificationEvent",
        docstring='"""Common base class for Notification CC states enums."""',
    )
)

lines.extend(
    generate_int_enum_base_class(
        "NotificationEventValue",
        docstring='"""Common base class for Notification CC state value enums."""',
    )
)

# Add events that have enums

_notification_type_to_notification_event_map = {}
_notification_event_to_event_value_map = {}
for notification_type, event_map in notifications.items():
    notification_event_name = f"{notification_type} Notification Event"
    lines.extend(
        generate_int_enum_class_definition(
            format_for_class_name(notification_event_name),
            event_map["events"],
            NOTIFICATIONS_URL,
            docstring_info=notification_event_name.lower(),
            base_class="NotificationEvent",
            include_missing=True,
        )
    )
    _notification_type_to_notification_event_map[
        notification_type
    ] = format_for_class_name(notification_event_name)
    if notification_type in params:
        for event_name, event_values in params[notification_type].items():
            notification_event_value_name = f"{event_name} Notification Event Value"
            lines.extend(
                generate_int_enum_class_definition(
                    format_for_class_name(notification_event_value_name),
                    event_values,
                    NOTIFICATIONS_URL,
                    docstring_info=notification_event_value_name.lower(),
                    base_class="NotificationEventValue",
                    include_missing=True,
                )
            )
            _notification_event_to_event_value_map[
                f"{format_for_class_name(notification_event_name)}.{enum_name_format(event_name, False)}"
            ] = format_for_class_name(notification_event_value_name)

notification_type_to_notification_event_map = dict(
    sorted(_notification_type_to_notification_event_map.items(), key=lambda kv: kv[0])
)
notification_type_to_event_map_line = (
    "NOTIFICATION_TYPE_TO_EVENT_MAP: dict[NotificationType, "
    "type[NotificationEvent]] = {"
)
for (
    notification_type,
    notification_event,
) in notification_type_to_notification_event_map.items():
    notification_type_to_event_map_line += f"    NotificationType.{enum_name_format(notification_type, False)}: {notification_event},"
notification_type_to_event_map_line += "}"
lines.append(notification_type_to_event_map_line)
lines.append("")


notification_event_to_event_value_map = dict(
    sorted(_notification_event_to_event_value_map.items(), key=lambda kv: kv[0])
)
notification_event_to_event_value_map_line = (
    "NOTIFICATION_EVENT_TO_EVENT_VALUE_MAP: dict[NotificationEvent, "
    "type[NotificationEventValue]] = {"
)
for (
    notification_event,
    notification_event_value,
) in notification_event_to_event_value_map.items():
    notification_event_to_event_value_map_line += (
        f"    {notification_event}: {notification_event_value},"
    )
notification_event_to_event_value_map_line += "}"
lines.append(notification_event_to_event_value_map_line)
lines.append("")

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

existing_const_file = CONST_FILE_PATH.read_text(encoding="utf-8").splitlines()

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

CONST_FILE_PATH.write_text("\n".join(lines), encoding="utf-8")

if subprocess.run(["which", "black"], capture_output=True, check=True).stdout:
    subprocess.run(
        ["black", CONST_FILE_PATH],
        check=True,
    )
else:
    print("Could not run black on new file, please run it to properly format it.")

if subprocess.run(["which", "git"], capture_output=True, check=True).stdout:
    if (
        subprocess.run(
            ["git", "diff", "--stat"],
            check=True,
        ).stdout
        is not None
    ):
        print("Repo is dirty and needs to be committed!")
        sys.exit(1)
else:
    print(
        "Could not run `git diff --stat` on repo, please run it to determine whether "
        "constants have changed."
    )
