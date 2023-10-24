"""
Constants for lock related CCs.

Includes Door Lock and Lock CCs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import TypedDict

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


class DoorLockCCConfigurationSetOptionsDataType(TypedDict, total=False):
    """Door Lock CC Configuration Set command options."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/cc/src/cc/DoorLockCC.ts#L1156
    operationType: int  # required
    lockTimeoutConfiguration: int
    outsideHandlesCanOpenDoorConfiguration: list[bool]  # required when from device
    insideHandlesCanOpenDoorConfiguration: list[bool]  # required when from device
    autoRelockTime: int
    holdAndReleaseTime: int
    twistAssist: bool
    blockToBlock: bool


DEFAULT_HANDLE_CONFIGURATION = [True, True, True, True]


@dataclass
class DoorLockCCConfigurationSetOptions:
    """Door Lock CC Configuration Set command options."""

    operation_type: OperationType
    lock_timeout_configuration: int | None = None
    outside_handles_can_open_door_configuration: list[bool] = field(
        default_factory=list
    )
    inside_handles_can_open_door_configuration: list[bool] = field(default_factory=list)
    auto_relock_time: int | None = None
    hold_and_release_time: int | None = None
    twist_assist: bool | None = None
    block_to_block: bool | None = None

    def __post_init__(self) -> None:
        """Post initialization."""
        for attr_name in (
            "inside_handles_can_open_door_configuration",
            "outside_handles_can_open_door_configuration",
        ):
            if not getattr(self, attr_name):
                setattr(self, attr_name, DEFAULT_HANDLE_CONFIGURATION)

    def to_dict(self) -> DoorLockCCConfigurationSetOptionsDataType:
        """Convert command options to dict."""
        data = DoorLockCCConfigurationSetOptionsDataType(
            operationType=self.operation_type,
            outsideHandlesCanOpenDoorConfiguration=(
                self.outside_handles_can_open_door_configuration
            ),
            insideHandlesCanOpenDoorConfiguration=(
                self.inside_handles_can_open_door_configuration
            ),
        )
        for prop_name, val in (
            (TARGET_AUTO_RELOCK_TIME_PROPERTY, self.auto_relock_time),
            (TARGET_HOLD_AND_RELEASE_TIME_PROPERTY, self.hold_and_release_time),
            (TARGET_TWIST_ASSIST_PROPERTY, self.twist_assist),
            (TARGET_BLOCK_TO_BLOCK_PROPERTY, self.block_to_block),
        ):
            if val is not None:
                data[prop_name] = val  # type: ignore[literal-required]

        return data
