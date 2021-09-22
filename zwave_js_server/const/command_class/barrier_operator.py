"""Constants for the Barrier Operator CC."""
from enum import IntEnum

SIGNALING_STATE_PROPERTY = "signalingState"


class BarrierEventSignalingSubsystemState(IntEnum):
    """Enum with all (known/used) Z-Wave Barrier Event Signaling Subsystem States."""

    # https://github.com/zwave-js/node-zwave-js/blob/15e1b59f627bfad8bfae114bd774a14089c76683/packages/zwave-js/src/lib/commandclass/BarrierOperatorCC.ts#L46-L49
    OFF = 0
    ON = 255


class BarrierState(IntEnum):
    """Enum with all (known/used) Z-Wave Barrier States."""

    # https://github.com/zwave-js/node-zwave-js/blob/15e1b59f627bfad8bfae114bd774a14089c76683/packages/zwave-js/src/lib/commandclass/BarrierOperatorCC.ts#L107-L113
    CLOSED = 0
    CLOSING = 252
    STOPPED = 253
    OPENING = 254
    OPEN = 255
