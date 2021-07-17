"""Utility functions for Z-Wave JS locks."""
from typing import Dict, List, Optional, Union

from ..const import (
    ATTR_CODE_SLOT,
    ATTR_ENDPOINT,
    ATTR_IN_USE,
    ATTR_NAME,
    ATTR_USERCODE,
    LOCK_USERCODE_PROPERTY,
    LOCK_USERCODE_STATUS_PROPERTY,
    CodeSlotStatus,
    CommandClass,
)
from ..exceptions import NotFoundError
from ..model.node import Node
from ..model.value import Value, get_value_id


def get_code_slot_value(node: Node, code_slot: int, property_name: str) -> Value:
    """Get a code slot value."""
    value = node.values.get(
        get_value_id(
            node,
            CommandClass.USER_CODE,
            property_name,
            endpoint=0,
            property_key=code_slot,
        )
    )

    if not value:
        raise NotFoundError(f"{property_name} for code slot {code_slot} not found")

    return value


def _get_code_slots(
    node: Node, include_usercode: bool = False
) -> List[Dict[str, Optional[Union[int, bool, str]]]]:
    """Get all code slots on the lock and optionally include usercode."""
    code_slot = 1
    slots: List[Dict[str, Optional[Union[int, bool, str]]]] = []

    # Loop until we can't find a code slot
    while True:
        try:
            value = get_code_slot_value(node, code_slot, LOCK_USERCODE_PROPERTY)
            status_value = get_code_slot_value(
                node, code_slot, LOCK_USERCODE_STATUS_PROPERTY
            )
        except NotFoundError:
            return slots

        code_slot = int(value.property_key)  # type: ignore

        # we know that code slots will always have a property key
        # that is an int, so we can ignore mypy
        slot = {
            ATTR_CODE_SLOT: code_slot,
            ATTR_ENDPOINT: value.endpoint,
            ATTR_NAME: value.metadata.label,
            ATTR_IN_USE: status_value.value == CodeSlotStatus.ENABLED,
        }
        if include_usercode:
            slot[ATTR_USERCODE] = value.value

        slots.append(slot)
        code_slot += 1


def get_code_slots(node: Node) -> List[Dict[str, Optional[Union[int, bool, str]]]]:
    """Get all code slots on the lock and whether or not they are used."""
    return _get_code_slots(node, False)


def get_usercodes(node: Node) -> List[Dict[str, Optional[Union[int, bool, str]]]]:
    """Get all code slots and usercodes on the lock."""
    return _get_code_slots(node, True)


def get_usercode(node: Node, code_slot: int) -> Optional[str]:
    """Get usercode from slot X on the lock."""
    value = get_code_slot_value(node, code_slot, LOCK_USERCODE_PROPERTY)
    return value.value


async def populate_usercode_in_value_db(node: Node, code_slot: int) -> None:
    """Fetch a usercode from a node to store in Z-Wave JS's ValueDB."""
    endpoint = get_code_slot_value(node, code_slot, LOCK_USERCODE_PROPERTY).endpoint
    # We can do this because every value has an endpoint and an exception will be
    # raised if the zwave value can't be found
    assert endpoint
    await node.endpoints[endpoint].async_invoke_cc_api(
        CommandClass.USER_CODE, "get", code_slot
    )


async def set_usercode(node: Node, code_slot: int, usercode: str) -> None:
    """Set the usercode to index X on the lock."""
    value = get_code_slot_value(node, code_slot, LOCK_USERCODE_PROPERTY)

    if len(str(usercode)) < 4:
        raise ValueError("User code must be at least 4 digits")

    await node.async_set_value(value, usercode)


async def clear_usercode(node: Node, code_slot: int) -> None:
    """Clear a code slot on the lock."""
    value = get_code_slot_value(node, code_slot, LOCK_USERCODE_STATUS_PROPERTY)
    await node.async_set_value(value, CodeSlotStatus.AVAILABLE.value)
