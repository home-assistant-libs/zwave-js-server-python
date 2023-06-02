"""
Constants for lock related CCs.

Includes Door Lock and Lock CCs.
"""
from __future__ import annotations

from enum import Enum, IntEnum

from .. import CommandClass


class DoorLockMode(IntEnum):
    """Enum with all (known/used) Z-Wave lock states for CommandClass.DOOR_LOCK."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/DoorLockCC.ts#L56-L65
    UNSECURED = 0
    UNSECURED_WITH_TIMEOUT = 1
    INSIDE_UNSECURED = 2
    INSIDE_UNSECURED_WITH_TIMEOUT = 3
    OUTSIDE_UNSECURED = 4
    OUTSIDE_UNSECURED_WITH_TIMEOUT = 5
    UNKNOWN = 254
    SECURED = 255


class OperationType(IntEnum):
    """Enum with all (known/used) Z-Wave lock operation types."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/cc/src/lib/_Types.ts#L496
    CONSTANT = 1
    TIMED = 2


DOOR_LOCK_CC_UNSECURED_MAP = {
    OperationType.CONSTANT: {
        DoorLockMode.UNSECURED,
        DoorLockMode.INSIDE_UNSECURED,
        DoorLockMode.OUTSIDE_UNSECURED,
    },
    OperationType.TIMED: {
        DoorLockMode.UNSECURED_WITH_TIMEOUT,
        DoorLockMode.INSIDE_UNSECURED_WITH_TIMEOUT,
        DoorLockMode.OUTSIDE_UNSECURED_WITH_TIMEOUT,
    },
}


class LatchStatus(str, Enum):
    """Enum with all (known/used) Z-Wave latch statuses."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/cc/src/cc/DoorLockCC.ts#L854
    OPEN = "open"
    CLOSED = "closed"


class BoltStatus(str, Enum):
    """Enum with all (known/used) Z-Wave bolt statuses."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/cc/src/cc/DoorLockCC.ts#L854
    LOCKED = "locked"
    UNLOCKED = "unlocked"


class DoorStatus(str, Enum):
    """Enum with all (known/used) Z-Wave door statuses."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/cc/src/cc/DoorLockCC.ts#L854
    OPEN = "open"
    CLOSED = "closed"


class CodeSlotStatus(IntEnum):
    """Enum with all (known/used) Z-Wave code slot statuses."""

    AVAILABLE = 0
    ENABLED = 1
    DISABLED = 2


# Depending on the Command Class being used by the lock, the lock state is
# different so we need a map to track it
LOCK_CMD_CLASS_TO_LOCKED_STATE_MAP = {
    CommandClass.DOOR_LOCK: DoorLockMode.SECURED,
    CommandClass.LOCK: True,
}

# Door Lock CC value constants
BOLT_STATUS_PROPERTY = "boltStatus"
CURRENT_AUTO_RELOCK_TIME_PROPERTY = "autoRelockTime"
CURRENT_BLOCK_TO_BLOCK_PROPERTY = "blockToBlock"
CURRENT_HOLD_AND_RELEASE_TIME_PROPERTY = "holdAndReleaseTime"
CURRENT_INSIDE_HANDLES_CAN_OPEN_DOOR_PROPERTY = "insideHandlesCanOpenDoor"
CURRENT_LOCK_TIMEOUT_PROPERTY = "lockTimeout"
CURRENT_MODE_PROPERTY = "currentMode"
CURRENT_OPERATION_TYPE_PROPERTY = "operationType"
CURRENT_OUTSIDE_HANDLES_CAN_OPEN_DOOR_PROPERTY = "outsideHandlesCanOpenDoor"
CURRENT_TWIST_ASSIST_PROPERTY = "twistAssist"
DOOR_STATUS_PROPERTY = "doorStatus"
LATCH_STATUS_PROPERTY = "latchStatus"
TARGET_MODE_PROPERTY = "targetMode"

# Door Lock CC configuration constants
TARGET_AUTO_RELOCK_TIME_PROPERTY = CURRENT_AUTO_RELOCK_TIME_PROPERTY
TARGET_BLOCK_TO_BLOCK_PROPERTY = CURRENT_BLOCK_TO_BLOCK_PROPERTY
TARGET_HOLD_AND_RELEASE_TIME_PROPERTY = CURRENT_HOLD_AND_RELEASE_TIME_PROPERTY
TARGET_INSIDE_HANDLES_CAN_OPEN_DOOR_PROPERTY = "insideHandlesCanOpenDoorConfiguration"
TARGET_LOCK_TIMEOUT_PROPERTY = "lockTimeoutConfiguration"
TARGET_OPERATION_TYPE_PROPERTY = CURRENT_OPERATION_TYPE_PROPERTY
TARGET_OUTSIDE_HANDLES_CAN_OPEN_DOOR_PROPERTY = "outsideHandlesCanOpenDoorConfiguration"
TARGET_TWIST_ASSIST_PROPERTY = CURRENT_TWIST_ASSIST_PROPERTY

# Lock CC constants
LOCKED_PROPERTY = "locked"

# User Code CC constants
LOCK_USERCODE_PROPERTY = "userCode"
LOCK_USERCODE_STATUS_PROPERTY = "userIdStatus"

ATTR_CODE_SLOT = "code_slot"
ATTR_IN_USE = "in_use"
ATTR_NAME = "name"
ATTR_USERCODE = "usercode"

# Depending on the Command Class being used by the lock, the locked state property
# is different so we need a map to track it
LOCK_CMD_CLASS_TO_PROPERTY_MAP = {
    CommandClass.DOOR_LOCK: TARGET_MODE_PROPERTY,
    CommandClass.LOCK: LOCKED_PROPERTY,
}
