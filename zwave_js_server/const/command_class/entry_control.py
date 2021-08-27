"""Constants for the Entry Control CC."""
from enum import IntEnum


class EntryControlEventType(IntEnum):
    """Entry control event types."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/EntryControlCC.ts#L54
    CACHING = 0
    CACHED_KEYS = 1
    ENTER = 2
    DISARM_ALL = 3
    ARM_ALL = 4
    ARM_AWAY = 5
    ARM_HOME = 6
    EXIT_DELAY = 7
    ARM1 = 8
    ARM2 = 9
    ARM3 = 10
    ARM4 = 11
    ARM5 = 12
    ARM6 = 13
    RFID = 14
    BELL = 15
    FIRE = 16
    POLICE = 17
    ALERT_PANIC = 18
    ALERT_MEDICAL = 19
    GATE_OPEN = 20
    GATE_CLOSE = 21
    LOCK = 22
    UNLOCK = 23
    TEST = 24
    CANCEL = 25


class EntryControlDataType(IntEnum):
    """Entry control data types."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/EntryControlCC.ts#L83
    NONE = 0
    RAW = 1
    ASCII = 2
    MD5 = 3
