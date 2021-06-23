"""Constants for the Z-Wave JS python library."""
from enum import Enum, IntEnum
from typing import Dict, List

# minimal server schema version we can handle
MIN_SERVER_SCHEMA_VERSION = 6
# max server schema version we can handle (and our code is compatible with)
MAX_SERVER_SCHEMA_VERSION = 6

VALUE_UNKNOWN = "unknown"

INTERVIEW_FAILED = "Failed"


class CommandStatus(str, Enum):
    """Status of a command sent to zwave-js-server."""

    ACCEPTED = "accepted"
    QUEUED = "queued"


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


class ProtocolVersion(IntEnum):
    """Protocol version."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/Types.ts#L149
    UNKNOWN = 0
    VERSION_2_0 = 1
    VERSION_4_2X_OR_5_0X = 2
    VERSION_4_5X_OR_6_0X = 3


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

    ALARM = 113
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


# Lock constants
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


class CodeSlotStatus(IntEnum):
    """Enum with all (known/used) Z-Wave code slot statuses."""

    AVAILABLE = 0
    ENABLED = 1
    DISABLED = 2


# Depending on the Command Class being used by the lock, the lock state is
# different so we need a map to track it
LOCK_CMD_CLASS_TO_LOCKED_STATE_MAP = {
    CommandClass.DOOR_LOCK: DoorLockMode.SECURED,
    CommandClass.LOCK: 1,
}

# Depending on the Command Class being used by the lock, the locked state property
# is different so we need a map to track it
LOCK_CMD_CLASS_TO_PROPERTY_MAP = {
    CommandClass.DOOR_LOCK: "targetMode",
    CommandClass.LOCK: "locked",
}

LOCK_USERCODE_PROPERTY = "userCode"
LOCK_USERCODE_STATUS_PROPERTY = "userIdStatus"
ATTR_CODE_SLOT = "code_slot"
ATTR_IN_USE = "in_use"
ATTR_NAME = "name"
ATTR_USERCODE = "usercode"


# Thermostat constants
THERMOSTAT_MODE_PROPERTY = "mode"
THERMOSTAT_SETPOINT_PROPERTY = "setpoint"
THERMOSTAT_OPERATING_STATE_PROPERTY = "state"
THERMOSTAT_CURRENT_TEMP_PROPERTY = "Air temperature"


class ThermostatMode(IntEnum):
    """Enum with all (known/used) Z-Wave ThermostatModes."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/ThermostatModeCC.ts#L53-L70
    OFF = 0
    HEAT = 1
    COOL = 2
    AUTO = 3
    AUXILIARY = 4
    RESUME_ON = 5
    FAN = 6
    FURNANCE = 7
    DRY = 8
    MOIST = 9
    AUTO_CHANGE_OVER = 10
    HEATING_ECON = 11
    COOLING_ECON = 12
    AWAY = 13
    FULL_POWER = 15
    MANUFACTURER_SPECIFIC = 31


class ThermostatOperatingState(IntEnum):
    """Enum with all (known/used) Z-Wave Thermostat OperatingStates."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/ThermostatOperatingStateCC.ts#L38-L51
    IDLE = 0
    HEATING = 1
    COOLING = 2
    FAN_ONLY = 3
    PENDING_HEAT = 4
    PENDING_COOL = 5
    VENT_ECONOMIZER = 6
    AUX_HEATING = 7
    SECOND_STAGE_HEATING = 8
    SECOND_STAGE_COOLING = 9
    SECOND_STAGE_AUX_HEAT = 10
    THIRD_STAGE_AUX_HEAT = 11


class ThermostatSetpointType(IntEnum):
    """
    Enum with all (known/used) Z-Wave Thermostat Setpoint Types.

    Returns tuple of (property_key, property_key_name).
    """

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/ThermostatSetpointCC.ts#L53-L66
    NA = 0
    HEATING = 1
    COOLING = 2
    FURNACE = 7
    DRY_AIR = 8
    MOIST_AIR = 9
    AUTO_CHANGEOVER = 10
    ENERGY_SAVE_HEATING = 11
    ENERGY_SAVE_COOLING = 12
    AWAY_HEATING = 13
    AWAY_COOLING = 14
    FULL_POWER = 15


# In Z-Wave the modes and presets are both in ThermostatMode.
# This list contains thermostatmodes we should consider a mode only
THERMOSTAT_MODES = [
    ThermostatMode.OFF,
    ThermostatMode.HEAT,
    ThermostatMode.COOL,
    ThermostatMode.AUTO,
    ThermostatMode.AUTO_CHANGE_OVER,
]

THERMOSTAT_MODE_SETPOINT_MAP: Dict[int, List[ThermostatSetpointType]] = {
    ThermostatMode.OFF: [],
    ThermostatMode.HEAT: [ThermostatSetpointType.HEATING],
    ThermostatMode.COOL: [ThermostatSetpointType.COOLING],
    ThermostatMode.AUTO: [
        ThermostatSetpointType.HEATING,
        ThermostatSetpointType.COOLING,
    ],
    ThermostatMode.AUXILIARY: [ThermostatSetpointType.HEATING],
    ThermostatMode.FURNANCE: [ThermostatSetpointType.FURNACE],
    ThermostatMode.DRY: [ThermostatSetpointType.DRY_AIR],
    ThermostatMode.MOIST: [ThermostatSetpointType.MOIST_AIR],
    ThermostatMode.AUTO_CHANGE_OVER: [ThermostatSetpointType.AUTO_CHANGEOVER],
    ThermostatMode.HEATING_ECON: [ThermostatSetpointType.ENERGY_SAVE_HEATING],
    ThermostatMode.COOLING_ECON: [ThermostatSetpointType.ENERGY_SAVE_COOLING],
    ThermostatMode.AWAY: [
        ThermostatSetpointType.AWAY_HEATING,
        ThermostatSetpointType.AWAY_COOLING,
    ],
    ThermostatMode.FULL_POWER: [ThermostatSetpointType.FULL_POWER],
}


class ConfigurationValueType(Enum):
    """Enum for configuration value types."""

    ENUMERATED = "enumerated"
    MANUAL_ENTRY = "manual_entry"
    RANGE = "range"
    UNDEFINED = "undefined"


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


class ColorComponent(IntEnum):
    """Enum with all (known/used) Color Switch CC colors."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/ColorSwitchCC.ts#L62
    WARM_WHITE = 0
    COLD_WHITE = 1
    RED = 2
    GREEN = 3
    BLUE = 4
    AMBER = 5
    CYAN = 6
    PURPLE = 7
    INDEX = 8
