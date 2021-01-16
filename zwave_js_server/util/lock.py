"""Utility functions for OpenZWave locks."""
from typing import Dict, List, Optional, Union

from ..const import (
    ATTR_CODE_SLOT,
    ATTR_IN_USE,
    ATTR_NAME,
    ATTR_USERCODE,
    LOCK_USERCODE_PROPERTY,
    CommandClass,
)
from ..exceptions import NotFoundError
from ..model.node import Node
from ..model.value import get_value_id


def _get_code_slots(
    node: Node, include_usercode: bool = False
) -> List[Dict[str, Optional[Union[int, bool, str]]]]:
    """Get all code slots on the lock and optionally include usercode."""
    code_slot = 1
    slots = []

    # Loop until we can't find a code slot
    while True:
        value_id = get_value_id(
            node,
            {
                "commandClass": CommandClass.USER_CODE,
                "property": LOCK_USERCODE_PROPERTY,
                "propertyKeyName": str(code_slot),
            },
        )
        value = node.values.get(value_id)
        if value:
            slot = {
                ATTR_CODE_SLOT: int(value.property_key),
                ATTR_NAME: value.metadata.label,
                ATTR_IN_USE: bool(value.value),
            }
            if include_usercode:
                slot[ATTR_USERCODE] = value.value if value.value else None

            slots.append(slot)
            code_slot += 1
        else:
            return slots


def get_code_slots(node: Node) -> List[Dict[str, Optional[Union[int, bool, str]]]]:
    """Get all code slots on the lock and whether or not they are used."""
    return _get_code_slots(node, False)


def get_usercodes(node: Node) -> List[Dict[str, Optional[Union[int, bool, str]]]]:
    """Get all code slots and usercodes on the lock."""
    return _get_code_slots(node, True)


def get_usercode(node: Node, code_slot: int) -> Optional[str]:
    """Get usercode from slot X on the lock."""
    value_id = get_value_id(
        node,
        {
            "commandClass": CommandClass.USER_CODE,
            "property": LOCK_USERCODE_PROPERTY,
            "propertyKeyName": str(code_slot),
        },
    )
    value = node.values.get(value_id)

    if not value:
        raise NotFoundError(f"Code slot {code_slot} not found")

    return str(value.value) if value.value else None


async def set_usercode(node: Node, code_slot: int, usercode: str) -> None:
    """Set the usercode to index X on the lock."""
    value_id = get_value_id(
        node,
        {
            "commandClass": CommandClass.USER_CODE,
            "property": LOCK_USERCODE_PROPERTY,
            "propertyKeyName": str(code_slot),
        },
    )
    value = node.values.get(value_id)

    if not value:
        raise NotFoundError(f"Code slot {code_slot} not found")

    if len(str(usercode)) < 4:
        raise ValueError("User code must be at least 4 digits")

    await node.async_set_value(value, usercode)
