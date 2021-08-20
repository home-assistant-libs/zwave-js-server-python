"""Constants for the Z-Wave JS python library."""
from enum import Enum, IntEnum
from typing import Dict, List, Set, Type, Union

# minimal server schema version we can handle
MIN_SERVER_SCHEMA_VERSION = 8
# max server schema version we can handle (and our code is compatible with)
MAX_SERVER_SCHEMA_VERSION = 8

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
THERMOSTAT_HUMIDITY_PROPERTY = "Humidity"


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


COVER_OPEN_PROPERTY = "Open"
COVER_UP_PROPERTY = "Up"
COVER_ON_PROPERTY = "On"
COVER_CLOSE_PROPERTY = "Close"
COVER_DOWN_PROPERTY = "Down"
COVER_OFF_PROPERTY = "Off"


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


# Keys for the Color Switch CC combined colors value
# https://github.com/zwave-js/node-zwave-js/pull/1782
COLOR_SWITCH_COMBINED_RED = "red"
COLOR_SWITCH_COMBINED_GREEN = "green"
COLOR_SWITCH_COMBINED_BLUE = "blue"
COLOR_SWITCH_COMBINED_AMBER = "amber"
COLOR_SWITCH_COMBINED_CYAN = "cyan"
COLOR_SWITCH_COMBINED_PURPLE = "purple"
COLOR_SWITCH_COMBINED_WARM_WHITE = "warmWhite"
COLOR_SWITCH_COMBINED_COLD_WHITE = "coldWhite"

CURRENT_COLOR_PROPERTY = "currentColor"
TARGET_COLOR_PROPERTY = "targetColor"
TARGET_STATE_PROPERTY = "targetState"
TARGET_VALUE_PROPERTY = "targetValue"


class ToneID(IntEnum):
    """Enum with all known Sound Switch CC tone IDs."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/SoundSwitchCC.ts#L71
    OFF = 0
    DEFAULT = 255


class NodeStatus(IntEnum):
    """Enum with all Node status values."""

    # https://zwave-js.github.io/node-zwave-js/#/api/node?id=status
    UNKNOWN = 0
    ASLEEP = 1
    AWAKE = 2
    DEAD = 3
    ALIVE = 4


CC_SPECIFIC_SCALE = "scale"


# Multilevel Sensor constants
CC_SPECIFIC_SENSOR_TYPE = "sensorType"


class MultilevelSensorType(IntEnum):
    """Enum with all known multilevel sensor types."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    AIR_TEMPERATURE = 1
    GENERAL_PURPOSE = 2
    ILLUMINANCE = 3
    POWER = 4
    HUMIDITY = 5
    VELOCITY = 6
    DIRECTION = 7
    ATMOSPHERIC_PRESSURE = 8
    BAROMETRIC_PRESSURE = 9
    SOLAR_RADIATION = 10
    DEW_POINT = 11
    RAIN_RATE = 12
    TIDE_LEVEL = 13
    WEIGHT = 14
    VOLTAGE = 15
    CURRENT = 16
    CARBON_DIOXIDE_LEVEL = 17
    AIR_FLOW = 18
    TANK_CAPACITY = 19
    DISTANCE = 20
    ANGLE_POSITION = 21
    ROTATION = 22
    WATER_TEMPERATURE = 23
    SOIL_TEMPERATURE = 24
    SEISMIC_INTENSITY = 25
    SEISMIC_MAGNITUDE = 26
    ULTRAVIOLET = 27
    ELECTRICAL_RESISTIVITY = 28
    ELECTRICAL_CONDUCTIVITY = 29
    LOUDNESS = 30
    MOISTURE = 31
    FREQUENCY = 32
    TIME = 33
    TARGET_TEMPERATURE = 34
    PARTICULATE_MATTER_25 = 35
    FORMALDEHYDE_LEVEL = 36
    RADON_CONCENTRATION = 37
    METHANE_DENSITY = 38
    VOLATILE_ORGANIC_COMPOUND_LEVEL = 39
    CARBON_MONOXIDE_LEVEL = 40
    SOIL_HUMIDITY = 41
    SOIL_REACTIVITY = 42
    SOIL_SALINITY = 43
    HEART_RATE = 44
    BLOOD_PRESSURE = 45
    MUSCLE_MASS = 46
    FAT_MASS = 47
    BONE_MASS = 48
    TOTAL_BODY_WATER = 49
    BASIS_METABOLIC_RATE = 50
    BODY_MASS_INDEX = 51
    ACCELERATION_X_AXIS = 52
    ACCELERATION_Y_AXIS = 53
    ACCELERATION_Z_AXIS = 54
    SMOKE_DENSITY = 55
    WATER_FLOW = 56
    WATER_PRESSURE = 57
    RF_SIGNAL_STRENGTH = 58
    PARTICULATE_MATTER_10 = 59
    RESPIRATORY_RATE = 60
    RELATIVE_MODULATION_LEVEL = 61
    BOILER_WATER_TEMPERATURE = 62
    DOMESTIC_HOT_WATER_TEMPERATURE = 63
    OUTSIDE_TEMPERATURE = 64
    EXHAUST_TEMPERATURE = 65
    WATER_CHLORINE_LEVEL = 66
    WATER_ACIDITY = 67
    WATER_OXIDATION_REDUCTION_POTENTIAL = 68
    HEART_RATE_LF_HF_RATIO = 69
    MOTION_DIRECTION = 70
    APPLIED_FORCE_ON_THE_SENSOR = 71
    RETURN_AIR_TEMPERATURE = 72
    SUPPLY_AIR_TEMPERATURE = 73
    CONDENSER_COIL_TEMPERATURE = 74
    EVAPORATOR_COIL_TEMPERATURE = 75
    LIQUID_LINE_TEMPERATURE = 76
    DISCHARGE_LINE_TEMPERATURE = 77
    SUCTION_PRESSURE = 78
    DISCHARGE_PRESSURE = 79
    DEFROST_TEMPERATURE = 80
    OZONE = 81
    SULFUR_DIOXIDE = 82
    NITROGEN_DIOXIDE = 83
    AMMONIA = 84
    LEAD = 85
    PARTICULATE_MATTER_1 = 86


CO_SENSORS = {MultilevelSensorType.CARBON_MONOXIDE_LEVEL}
CO2_SENSORS = {MultilevelSensorType.CARBON_DIOXIDE_LEVEL}
CURRENT_SENSORS = {MultilevelSensorType.CURRENT}
ENERGY_SENSORS = {MultilevelSensorType.BASIS_METABOLIC_RATE}
HUMIDITY_SENSORS = {MultilevelSensorType.HUMIDITY}
ILLUMINANCE_SENSORS = {MultilevelSensorType.ILLUMINANCE}
POWER_SENSORS = {MultilevelSensorType.POWER}
PRESSURE_SENSORS = {
    MultilevelSensorType.BLOOD_PRESSURE,
    MultilevelSensorType.WATER_PRESSURE,
    MultilevelSensorType.SUCTION_PRESSURE,
    MultilevelSensorType.DISCHARGE_PRESSURE,
    MultilevelSensorType.BAROMETRIC_PRESSURE,
    MultilevelSensorType.ATMOSPHERIC_PRESSURE,
}
SIGNAL_STRENGTH_SENSORS = {MultilevelSensorType.RF_SIGNAL_STRENGTH}
TEMPERATURE_SENSORS = {
    MultilevelSensorType.AIR_TEMPERATURE,
    MultilevelSensorType.DEW_POINT,
    MultilevelSensorType.WATER_TEMPERATURE,
    MultilevelSensorType.SOIL_TEMPERATURE,
    MultilevelSensorType.TARGET_TEMPERATURE,
    MultilevelSensorType.BOILER_WATER_TEMPERATURE,
    MultilevelSensorType.DOMESTIC_HOT_WATER_TEMPERATURE,
    MultilevelSensorType.OUTSIDE_TEMPERATURE,
    MultilevelSensorType.EXHAUST_TEMPERATURE,
    MultilevelSensorType.RETURN_AIR_TEMPERATURE,
    MultilevelSensorType.SUPPLY_AIR_TEMPERATURE,
    MultilevelSensorType.CONDENSER_COIL_TEMPERATURE,
    MultilevelSensorType.EVAPORATOR_COIL_TEMPERATURE,
    MultilevelSensorType.LIQUID_LINE_TEMPERATURE,
    MultilevelSensorType.DISCHARGE_LINE_TEMPERATURE,
    MultilevelSensorType.DEFROST_TEMPERATURE,
}
TIMESTAMP_SENSORS = {MultilevelSensorType.TIME}
VOLTAGE_SENSORS = {
    MultilevelSensorType.VOLTAGE,
    MultilevelSensorType.WATER_OXIDATION_REDUCTION_POTENTIAL,
}


# Meter CC constants

CC_SPECIFIC_METER_TYPE = "meterType"
CC_SPECIFIC_RATE_TYPE = "rateType"

RESET_METER_CC_API = "reset"

# optional attributes when calling the Meter CC reset API.
# https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/commandclass/MeterCC.ts#L873-L881
RESET_METER_OPTION_TARGET_VALUE = TARGET_VALUE_PROPERTY
RESET_METER_OPTION_TYPE = "type"


# https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/meters.json
class MeterType(IntEnum):
    """Enum with all known meter types."""

    ELECTRIC = 1
    GAS = 2
    WATER = 3
    HEATING = 4
    COOLING = 5


class ElectricScale(IntEnum):
    """Enum with all known electric meter scale values."""

    KILOWATT_HOUR = 0
    KILOVOLT_AMPERE_HOUR = 1
    WATT = 2
    PULSE = 3
    VOLT = 4
    AMPERE = 5
    POWER_FACTOR = 6
    KILOVOLT_AMPERE_REACTIVE = 7
    KILOVOLT_AMPERE_REACTIVE_HOUR = 8


class GasScale(IntEnum):
    """Enum with all known gas meter scale values."""

    CUBIC_METER = 0
    CUBIC_FEET = 1
    PULSE_COUNT = 3


class WaterScale(IntEnum):
    """Enum with all known water meter scale values."""

    CUBIC_METER = 0
    CUBIC_FEET = 1
    US_GALLON = 2
    PULSE_COUNT = 3


class HeatingScale(IntEnum):
    """Enum with all known heating meter scale values."""

    KILOWATT_HOUR = 0


CoolingScale = HeatingScale

MeterScaleType = Union[CoolingScale, ElectricScale, GasScale, HeatingScale, WaterScale]

METER_TYPE_TO_SCALE_ENUM_MAP: Dict[MeterType, Type[MeterScaleType]] = {
    MeterType.ELECTRIC: ElectricScale,
    MeterType.GAS: GasScale,
    MeterType.WATER: WaterScale,
    MeterType.HEATING: HeatingScale,
    MeterType.COOLING: CoolingScale,
}

ENERGY_METER_TYPES: Set[MeterScaleType] = {
    ElectricScale.KILOWATT_HOUR,
    ElectricScale.KILOVOLT_AMPERE_HOUR,
    ElectricScale.KILOVOLT_AMPERE_REACTIVE_HOUR,
    HeatingScale.KILOWATT_HOUR,
    CoolingScale.KILOWATT_HOUR,
}
POWER_METER_TYPES: Set[MeterScaleType] = {
    ElectricScale.WATT,
    ElectricScale.PULSE,
    ElectricScale.KILOVOLT_AMPERE_REACTIVE,
}
POWER_FACTOR_METER_TYPES: Set[MeterScaleType] = {ElectricScale.POWER_FACTOR}
VOLTAGE_METER_TYPES: Set[MeterScaleType] = {ElectricScale.VOLT}
CURRENT_METER_TYPES: Set[MeterScaleType] = {ElectricScale.AMPERE}


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
