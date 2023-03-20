"""Constants for the Power Level Command Class."""
from __future__ import annotations

from enum import IntEnum


class PowerLevelTestStatus(IntEnum):
    """Enum with all known power level test statuses."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/PowerlevelCC.ts#L52
    FAILED = 0
    SUCCESS = 1
    IN_PROGRESS = 2
