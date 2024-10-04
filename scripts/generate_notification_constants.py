#!/usr/bin/env python3
"""Script to generate Notification CC constants."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import pathlib

from const import AUTO_GEN_POST, AUTO_GEN_PRE
from helpers import (
    enum_name_format,
    format_for_class_name,
    get_json,
    get_manually_written_code,
    get_registry_location,
    run_black,
)

CONST_FILE_PATH = (
    pathlib.Path(__file__).parent.parent
    / "zwave_js_server/const/command_class/notification.py"
)

notifications = {}
params = {}
for notification_payload in get_json("notifications.json"):
    notification_type = notification_payload["type"]
    notification_name = notification_payload["name"].title()
    notifications[notification_name] = {
        "type": notification_type,
        "events": {},
    }
    for event in notification_payload.get("variables", []):
        event_name = event["name"].title()
        states = notifications[notification_name]["events"]
        for state_props in event["states"].values():
            state_id = state_props["value"]
            state_name = state_props["label"].title()
            if (
                state_name.lower() not in event_name.lower()
                and event_name.lower() not in state_name.lower()
            ):
                state_name = f"{event_name} {state_name}"
            states[state_name] = state_id
            if (
                "parameter" in state_props
                and state_props["parameter"]["type"] == "enum"
            ):
                for enum_id, enum_name in state_props["parameter"]["values"].items():
                    enum_id = int(enum_id)
                    params.setdefault(notification_name, {}).setdefault(state_name, {})[
                        enum_name.title()
                    ] = enum_id
    for event_data in notification_payload.get("events", {}).values():
        event_id = event_data["value"]
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
) -> list[str]:
    """Generate an IntEnum class definition as an array of lines of string."""
    class_def: list[str] = []
    class_def.append(f"class {class_name}({base_class}):")
    docstring = f'"""Enum for known {docstring_info}."""'.replace("  ", " ")
    class_def.append(f"    {docstring}")
    if enum_ref_url:
        class_def.append(f"    # {enum_ref_url}")
    class_def.append("    UNKNOWN = -1")
    for _enum_name, _enum_id in sorted(enum_map.items(), key=lambda x: x[0]):
        if get_id_func:
            _enum_id = get_id_func(_enum_id)
        class_def.append(f"    {enum_name_format(_enum_name, False)} = {_enum_id}")
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


NOTIFICATIONS_URL = get_registry_location("Notifications.ts")

lines = [
    "# pylint: disable=line-too-long",
    '"""Constants for the Notification CC."""',
    *AUTO_GEN_PRE,
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
        )
    )
    _notification_type_to_notification_event_map[notification_type] = (
        format_for_class_name(notification_event_name)
    )
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

lines.extend(AUTO_GEN_POST)
lines.extend(get_manually_written_code(CONST_FILE_PATH))
CONST_FILE_PATH.write_text("\n".join(lines), encoding="utf-8")

run_black(CONST_FILE_PATH)
