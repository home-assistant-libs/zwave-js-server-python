"""Constants for the Sound Switch CC."""
from enum import IntEnum

TONE_ID_PROPERTY = "toneId"
DEFAULT_TONE_ID_PROPERTY = "defaultToneId"
DEFAULT_VOLUME_PROPERTY = "defaultVolume"


class ToneID(IntEnum):
    """Enum with all known Sound Switch CC tone IDs."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/SoundSwitchCC.ts#L71
    OFF = 0
    DEFAULT = 255
