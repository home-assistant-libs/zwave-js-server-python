"""Constants for the Z-Wave JS python library."""
import sys
from enum import Enum, IntEnum
from importlib import metadata

PACKAGE_NAME = "zwave-js-server-python"
__version__ = metadata.version(PACKAGE_NAME)

# minimal server schema version we can handle
MIN_SERVER_SCHEMA_VERSION = 24
# max server schema version we can handle (and our code is compatible with)
MAX_SERVER_SCHEMA_VERSION = 24

TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED = sys.version_info < (3, 9, 2)

VALUE_UNKNOWN = "unknown"

NOT_INTERVIEWED = "None"
INTERVIEW_FAILED = "Failed"

CURRENT_STATE_PROPERTY = "currentState"
TARGET_STATE_PROPERTY = "targetState"
CURRENT_VALUE_PROPERTY = "currentValue"
TARGET_VALUE_PROPERTY = "targetValue"
DURATION_PROPERTY = "duration"

TRANSITION_DURATION_OPTION = "transitionDuration"
VOLUME_OPTION = "volume"


class CommandStatus(str, Enum):
    """Status of a command sent to zwave-js-server."""

    ACCEPTED = "accepted"
    QUEUED = "queued"


# Multiple inheritance so that LogLevel will JSON serialize properly
# Reference: https://stackoverflow.com/a/51976841
class LogLevel(str, Enum):
    """Enum for log levels used by node-zwave-js."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/core/src/log/shared.ts#L12
    # https://github.com/winstonjs/triple-beam/blame/master/config/npm.js#L14
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    HTTP = "http"
    VERBOSE = "verbose"
    DEBUG = "debug"
    SILLY = "silly"


class CommandClass(IntEnum):
    """Enum with all known CommandClasses."""

    SENSOR_ALARM = 156
    SILENCE_ALARM = 157
    SWITCH_ALL = 39
    ANTITHEFT = 93
    ANTITHEFT_UNLOCK = 126
    APPLICATION_CAPABILITY = 87
    APPLICATION_STATUS = 34
    ASSOCIATION = 133
    ASSOCIATION_COMMAND_CONFIGURATION = 155
    ASSOCIATION_GRP_INFO = 89
    AUTHENTICATION = 161
    AUTHENTICATION_MEDIA_WRITE = 162
    BARRIER_OPERATOR = 102
    BASIC = 32
    BASIC_TARIFF_INFO = 54
    BASIC_WINDOW_COVERING = 80
    BATTERY = 128
    SENSOR_BINARY = 48
    SWITCH_BINARY = 37
    SWITCH_TOGGLE_BINARY = 40
    CLIMATE_CONTROL_SCHEDULE = 70
    CENTRAL_SCENE = 91
    CLOCK = 129
    SWITCH_COLOR = 51
    CONFIGURATION = 112
    CONTROLLER_REPLICATION = 33
    CRC_16_ENCAP = 86
    DCP_CONFIG = 58
    DCP_MONITOR = 59
    DEVICE_RESET_LOCALLY = 90
    DOOR_LOCK = 98
    DOOR_LOCK_LOGGING = 76
    ENERGY_PRODUCTION = 144
    ENTRY_CONTROL = 111
    FIRMWARE_UPDATE_MD = 122
    GENERIC_SCHEDULE = 163
    GEOGRAPHIC_LOCATION = 140
    GROUPING_NAME = 123
    HAIL = 130
    HRV_STATUS = 55
    HRV_CONTROL = 57
    HUMIDITY_CONTROL_MODE = 109
    HUMIDITY_CONTROL_OPERATING_STATE = 110
    HUMIDITY_CONTROL_SETPOINT = 100
    INCLUSION_CONTROLLER = 116
    INDICATOR = 135
    IP_ASSOCIATION = 92
    IP_CONFIGURATION = 154
    IR_REPEATER = 160
    IRRIGATION = 107
    LANGUAGE = 137
    LOCK = 118
    MAILBOX = 105
    MANUFACTURER_PROPRIETARY = 145
    MANUFACTURER_SPECIFIC = 114
    MARK = 239
    METER = 50
    METER_TBL_CONFIG = 60
    METER_TBL_MONITOR = 61
    METER_TBL_PUSH = 62
    MTP_WINDOW_COVERING = 81
    MULTI_CHANNEL = 96
    MULTI_CHANNEL_ASSOCIATION = 142
    MULTI_CMD = 143
    SENSOR_MULTILEVEL = 49
    SWITCH_MULTILEVEL = 38
    SWITCH_TOGGLE_MULTILEVEL = 41
    NETWORK_MANAGEMENT_BASIC = 77
    NETWORK_MANAGEMENT_INCLUSION = 52
    NETWORK_MANAGEMENT_INSTALLATION_MAINTENANCE = 103
    NETWORK_MANAGEMENT_PRIMARY = 84
    NETWORK_MANAGEMENT_PROXY = 82
    NO_OPERATION = 0
    NODE_NAMING = 119
    NODE_PROVISIONING = 120
    NOTIFICATION = 113
    POWERLEVEL = 115
    PREPAYMENT = 63
    PREPAYMENT_ENCAPSULATION = 65
    PROPRIETARY = 136
    PROTECTION = 117
    METER_PULSE = 53
    RATE_TBL_CONFIG = 72
    RATE_TBL_MONITOR = 73
    REMOTE_ASSOCIATION_ACTIVATE = 124
    REMOTE_ASSOCIATION = 125
    SCENE_ACTIVATION = 43
    SCENE_ACTUATOR_CONF = 44
    SCENE_CONTROLLER_CONF = 45
    SCHEDULE = 83
    SCHEDULE_ENTRY_LOCK = 78
    SCREEN_ATTRIBUTES = 147
    SCREEN_MD = 146
    SECURITY = 152
    SECURITY_2 = 159
    SECURITY_SCHEME0_MARK = 61696
    SENSOR_CONFIGURATION = 158
    SIMPLE_AV_CONTROL = 148
    SOUND_SWITCH = 121
    SUPERVISION = 108
    TARIFF_CONFIG = 74
    TARIFF_TBL_MONITOR = 75
    THERMOSTAT_FAN_MODE = 68
    THERMOSTAT_FAN_STATE = 69
    THERMOSTAT_MODE = 64
    THERMOSTAT_OPERATING_STATE = 66
    THERMOSTAT_SETBACK = 71
    THERMOSTAT_SETPOINT = 67
    TIME = 138
    TIME_PARAMETERS = 139
    TRANSPORT_SERVICE = 85
    USER_CODE = 99
    VERSION = 134
    WAKE_UP = 132
    WINDOW_COVERING = 106
    ZIP = 35
    ZIP_6LOWPAN = 79
    ZIP_GATEWAY = 95
    ZIP_NAMING = 104
    ZIP_ND = 88
    ZIP_PORTAL = 97
    ZWAVEPLUS_INFO = 94


class ProtocolVersion(IntEnum):
    """Protocol version."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/Types.ts#L149
    UNKNOWN = 0
    VERSION_2_0 = 1
    VERSION_4_2X_OR_5_0X = 2
    VERSION_4_5X_OR_6_0X = 3


class NodeStatus(IntEnum):
    """Enum with all Node status values."""

    # https://zwave-js.github.io/node-zwave-js/#/api/node?id=status
    UNKNOWN = 0
    ASLEEP = 1
    AWAKE = 2
    DEAD = 3
    ALIVE = 4


class ConfigurationValueType(str, Enum):
    """Enum for configuration value types."""

    ENUMERATED = "enumerated"
    MANUAL_ENTRY = "manual_entry"
    RANGE = "range"
    UNDEFINED = "undefined"


class NodeType(IntEnum):
    """Enum with all Node types."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/core/src/capabilities/NodeInfo.ts#L151-L156
    CONTROLLER = 0
    END_NODE = 1


# Exclusion enums
class ExclusionStrategy(IntEnum):
    """Enum with all exclusion strategies."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/controller/Inclusion.ts#L49-L56
    EXCLUDE_ONLY = 0
    DISABLE_PROVISIONING_ENTRY = 1
    UNPROVISION = 2


# Inclusion enums
class InclusionStrategy(IntEnum):
    """Enum for all known inclusion strategies."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/controller/Inclusion.ts#L9-L46
    DEFAULT = 0
    SMART_START = 1
    INSECURE = 2
    SECURITY_S0 = 3
    SECURITY_S2 = 4


class SecurityClass(IntEnum):
    """Enum for all known security classes."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/core/src/security/SecurityClass.ts#L3-L17
    NONE = -1
    S2_UNAUTHENTICATED = 0
    S2_AUTHENTICATED = 1
    S2_ACCESS_CONTROL = 2
    S0_LEGACY = 7


class QRCodeVersion(IntEnum):
    """Enum for all known QR Code versions."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/core/src/security/QR.ts#L43-L46
    S2 = 0
    SMART_START = 1


class Protocols(IntEnum):
    """Enum for all known protocols."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/core/src/capabilities/Protocols.ts#L1-L4
    ZWAVE = 0
    ZWAVE_LONG_RANGE = 1


# https://github.com/zwave-js/node-zwave-js/blob/master/packages/core/src/security/QR.ts#L41
MINIMUM_QR_STRING_LENGTH = 52


class ZwaveFeature(IntEnum):
    """Enum for all known Zwave features."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/controller/Features.ts#L4
    SMART_START = 0


class PowerLevel(IntEnum):
    """Enum for all known power levels."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/PowerlevelCC.ts#L38
    NORMAL_POWER = 0
    DBM_MINUS_1 = 1
    DBM_MINUS_2 = 2
    DBM_MINUS_3 = 3
    DBM_MINUS_4 = 4
    DBM_MINUS_5 = 5
    DBM_MINUS_6 = 6
    DBM_MINUS_7 = 7
    DBM_MINUS_8 = 8
    DBM_MINUS_9 = 9


class InclusionState(IntEnum):
    """Enum for all known inclusion states."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/controller/Inclusion.ts#L154
    IDLE = 0
    INCLUDING = 1
    EXCLUDING = 2
    BUSY = 3
    SMART_START = 4


class RFRegion(IntEnum):
    """Enum for all known RF regions."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/serialapi/misc/SerialAPISetupMessages.ts#L41
    EUROPE = 0
    USA = 1
    AUSTRALIA_AND_NEW_ZEALAND = 2
    HONG_KONG = 3
    INDIA = 5
    ISRAEL = 6
    RUSSIA = 7
    CHINA = 8
    USA_LONG_RANGE = 9
    JAPAN = 32
    KOREA = 33
    UNKNOWN = 254
    DEFAULT_EU = 255


class ProtocolDataRate(IntEnum):
    """Enum for all known protocol data rates."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/core/src/capabilities/Protocols.ts#L6

    ZWAVE_9K6 = 1
    ZWAVE_40K = 2
    ZWAVE_100K = 3
    LONG_RANGE_100K = 4


class RssiError(IntEnum):
    """Enum for all known RSSI errors."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/controller/SendDataShared.ts#L79
    NOT_AVAILABLE = 127
    RECEIVER_SATURATED = 126
    NO_SIGNAL_DETECTED = 125


class ProvisioningEntryStatus(IntEnum):
    """Enum for all known provisioning entry statuses."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/controller/Inclusion.ts#L136
    ACTIVE = 0
    INACTIVE = 1
