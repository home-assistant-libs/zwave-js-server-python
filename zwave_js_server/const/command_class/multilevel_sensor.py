"""Constants for the Multilevel Sensor CC."""
from enum import IntEnum
from typing import Dict, Type, Union

CC_SPECIFIC_SCALE = "scale"
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
    PARTICULATE_MATTER_2_5 = 35
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
    PERSON_COUNTER_ENTERING = 87
    PERSON_COUNTER_EXITING = 88


class TemperatureScale(IntEnum):
    """Enum with all known scales for Temperature multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    CELSIUS = 0
    FAHRENHEIT = 1


class MassScale(IntEnum):
    """Enum with all known scales for Mass multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    KILOGRAM = 0


class AccelerationScale(IntEnum):
    """Enum with all known scales for Acceleration multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    METER_PER_SQUARE_SECOND = 0


class PercentageScale(IntEnum):
    """Enum with all known scales for Percentage multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    PERCENTAGE_VALUE = 0


class AcidityScale(IntEnum):
    """Enum with all known scales for Acidity multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    ACIDITY = 0


class DirectionScale(IntEnum):
    """Enum with all known scales for Direction multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    DEGREES = 0


class PressureScale(IntEnum):
    """Enum with all known scales for Pressure multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    KILOPASCAL = 0
    POUND_PER_SQUARE_INCH = 1


class AirPressureScale(IntEnum):
    """Enum with all known scales for Air Pressure multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    KILOPASCAL = 0
    INCHES_OF_MERCURY = 1


class DensityScale(IntEnum):
    """Enum with all known scales for Density multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    DENSITY = 0


class UnitlessScale(IntEnum):
    """Enum with all known scales for Unitless multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    UNITLESS = 0


class GeneralPurposeScale(IntEnum):
    """Enum with all known scales for GENERAL_PURPOSE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    PERCENTAGE_VALUE = 0
    DIMENSIONLESS_VALUE = 1


class IlluminanceScale(IntEnum):
    """Enum with all known scales for ILLUMINANCE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    PERCENTAGE_VALUE = 0
    LUX = 1


class PowerScale(IntEnum):
    """Enum with all known scales for POWER multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    WATT = 0
    BTU_H = 1


class HumidityScale(IntEnum):
    """Enum with all known scales for HUMIDITY multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    PERCENTAGE_VALUE = 0
    ABSOLUTE_HUMIDITY = 1


class VelocityScale(IntEnum):
    """Enum with all known scales for VELOCITY multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    M_S = 0
    MPH = 1


class SolarRadiationScale(IntEnum):
    """Enum with all known scales for SOLAR_RADIATION multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    WATT_PER_SQUARE_METER = 0


class RainRateScale(IntEnum):
    """Enum with all known scales for RAIN_RATE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MILLIMETER_HOUR = 0
    INCHES_PER_HOUR = 1


class TideLevelScale(IntEnum):
    """Enum with all known scales for TIDE_LEVEL multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    METER = 0
    FEET = 1


class WeightScale(IntEnum):
    """Enum with all known scales for WEIGHT multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    KILOGRAM = 0
    POUNDS = 1


class VoltageScale(IntEnum):
    """Enum with all known scales for VOLTAGE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    VOLT = 0
    MILLIVOLT = 1


class CurrentScale(IntEnum):
    """Enum with all known scales for CURRENT multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    AMPERE = 0
    MILLIAMPERE = 1


class CarbonDioxideLevelScale(IntEnum):
    """Enum with all known scales for CARBON_DIOXIDE_LEVEL multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    PARTS_MILLION = 0


class AirFlowScale(IntEnum):
    """Enum with all known scales for AIR_FLOW multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    CUBIC_METER_PER_HOUR = 0
    CUBIC_FEET_PER_MINUTE = 1


class TankCapacityScale(IntEnum):
    """Enum with all known scales for TANK_CAPACITY multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    LITER = 0
    CUBIC_METER = 1
    GALLONS = 2


class DistanceScale(IntEnum):
    """Enum with all known scales for DISTANCE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    METER = 0
    CENTIMETER = 1
    FEET = 2


class AnglePositionScale(IntEnum):
    """Enum with all known scales for ANGLE_POSITION multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    PERCENTAGE_VALUE = 0
    DEGREES_RELATIVE_TO_NORTH_POLE_OF_STANDING_EYE_VIEW = 1
    DEGREES_RELATIVE_TO_SOUTH_POLE_OF_STANDING_EYE_VIEW = 2


class RotationScale(IntEnum):
    """Enum with all known scales for ROTATION multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    REVOLUTIONS_PER_MINUTE = 0
    HERTZ = 1


class SeismicIntensityScale(IntEnum):
    """Enum with all known scales for SEISMIC_INTENSITY multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MERCALLI = 0
    EUROPEAN_MACROSEISMIC = 1
    LIEDU = 2
    SHINDO = 3


class SeismicMagnitudeScale(IntEnum):
    """Enum with all known scales for SEISMIC_MAGNITUDE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    LOCAL = 0
    MOMENT = 1
    SURFACE_WAVE = 2
    BODY_WAVE = 3


class UltravioletScale(IntEnum):
    """Enum with all known scales for ULTRAVIOLET multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    UV_INDEX = 0


class ElectricalResistivityScale(IntEnum):
    """Enum with all known scales for ELECTRICAL_RESISTIVITY multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    OHM_METER = 0


class ElectricalConductivityScale(IntEnum):
    """Enum with all known scales for ELECTRICAL_CONDUCTIVITY multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    SIEMENS_PER_METER = 0


class LoudnessScale(IntEnum):
    """Enum with all known scales for LOUDNESS multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    DECIBEL = 0
    A_WEIGHTED_DECIBELS = 1


class MoistureScale(IntEnum):
    """Enum with all known scales for MOISTURE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    PERCENTAGE_VALUE = 0
    VOLUME_WATER_CONTENT = 1
    IMPEDANCE = 2
    WATER_ACTIVITY = 3


class FrequencyScale(IntEnum):
    """Enum with all known scales for FREQUENCY multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    HERTZ = 0
    KILOHERTZ = 1


class TimeScale(IntEnum):
    """Enum with all known scales for TIME multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    SECOND = 0


class ParticulateMatter25Scale(IntEnum):
    """Enum with all known scales for PARTICULATE_MATTER_2_5 multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MOLE_PER_CUBIC_METER = 0
    MICROGRAM_PER_CUBIC_METER = 1


class FormaldehydeLevelScale(IntEnum):
    """Enum with all known scales for FORMALDEHYDE_LEVEL multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MOLE_PER_CUBIC_METER = 0


class RadonConcentrationScale(IntEnum):
    """Enum with all known scales for RADON_CONCENTRATION multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    BECQUEREL_PER_CUBIC_METER = 0
    PICOCURIES_PER_LITER = 1


class MethaneDensityScale(IntEnum):
    """Enum with all known scales for METHANE_DENSITY multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MOLE_PER_CUBIC_METER = 0


class VolatileOrganicCompoundLevelScale(IntEnum):
    """Enum with all known scales for VOLATILE_ORGANIC_COMPOUND_LEVEL multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MOLE_PER_CUBIC_METER = 0
    PARTS_MILLION = 1


class CarbonMonoxideLevelScale(IntEnum):
    """Enum with all known scales for CARBON_MONOXIDE_LEVEL multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MOLE_PER_CUBIC_METER = 0
    PARTS_MILLION = 1


class SoilSalinityScale(IntEnum):
    """Enum with all known scales for SOIL_SALINITY multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MOLE_PER_CUBIC_METER = 0


class HeartRateScale(IntEnum):
    """Enum with all known scales for HEART_RATE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    BEATS_PER_MINUTE = 0


class BloodPressureScale(IntEnum):
    """Enum with all known scales for BLOOD_PRESSURE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    SYSTOLIC = 0
    DIASTOLIC = 1


class BasisMetabolicRateScale(IntEnum):
    """Enum with all known scales for BASIS_METABOLIC_RATE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    JOULE = 0


class BodyMassIndexScale(IntEnum):
    """Enum with all known scales for BODY_MASS_INDEX multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    BODY_MASS_INDEX = 0


class WaterFlowScale(IntEnum):
    """Enum with all known scales for WATER_FLOW multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    LITER_PER_HOUR = 0


class WaterPressureScale(IntEnum):
    """Enum with all known scales for WATER_PRESSURE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    KILOPASCAL = 0


class RfSignalStrengthScale(IntEnum):
    """Enum with all known scales for RF_SIGNAL_STRENGTH multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    RSSI = 0
    POWER_LEVEL = 1


class ParticulateMatter10Scale(IntEnum):
    """Enum with all known scales for PARTICULATE_MATTER_10 multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MOLE_PER_CUBIC_METER = 0
    MICROGRAM_PER_CUBIC_METER = 1


class RespiratoryRateScale(IntEnum):
    """Enum with all known scales for RESPIRATORY_RATE multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    BREATHS_PER_MINUTE = 0


class WaterChlorineLevelScale(IntEnum):
    """Enum with all known scales for WATER_CHLORINE_LEVEL multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MILLIGRAM_PER_LITER = 0


class WaterOxidationReductionPotentialScale(IntEnum):
    """Enum with all known scales for WATER_OXIDATION_REDUCTION_POTENTIAL multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    MILLIVOLT = 0


class AppliedForceOnTheSensorScale(IntEnum):
    """Enum with all known scales for APPLIED_FORCE_ON_THE_SENSOR multilevel sensor type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/config/config/sensorTypes.json
    NEWTON = 0


MultilevelSensorScaleType = Union[
    AccelerationScale,
    AcidityScale,
    AirFlowScale,
    AirPressureScale,
    AnglePositionScale,
    AppliedForceOnTheSensorScale,
    BasisMetabolicRateScale,
    BloodPressureScale,
    BodyMassIndexScale,
    CarbonDioxideLevelScale,
    CarbonMonoxideLevelScale,
    CurrentScale,
    DensityScale,
    DirectionScale,
    DistanceScale,
    ElectricalConductivityScale,
    ElectricalResistivityScale,
    FormaldehydeLevelScale,
    FrequencyScale,
    GeneralPurposeScale,
    HeartRateScale,
    HumidityScale,
    IlluminanceScale,
    LoudnessScale,
    MassScale,
    MethaneDensityScale,
    MoistureScale,
    ParticulateMatter10Scale,
    ParticulateMatter25Scale,
    PercentageScale,
    PowerScale,
    PressureScale,
    RadonConcentrationScale,
    RainRateScale,
    RespiratoryRateScale,
    RfSignalStrengthScale,
    RotationScale,
    SeismicIntensityScale,
    SeismicMagnitudeScale,
    SoilSalinityScale,
    SolarRadiationScale,
    TankCapacityScale,
    TemperatureScale,
    TideLevelScale,
    TimeScale,
    UltravioletScale,
    UnitlessScale,
    VelocityScale,
    VolatileOrganicCompoundLevelScale,
    VoltageScale,
    WaterChlorineLevelScale,
    WaterFlowScale,
    WaterOxidationReductionPotentialScale,
    WaterPressureScale,
    WeightScale,
]

MULTILEVEL_SENSOR_TYPE_TO_SCALE_MAP: Dict[
    MultilevelSensorType, Type[MultilevelSensorScaleType]
] = {
    MultilevelSensorType.AIR_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.GENERAL_PURPOSE: GeneralPurposeScale,
    MultilevelSensorType.ILLUMINANCE: IlluminanceScale,
    MultilevelSensorType.POWER: PowerScale,
    MultilevelSensorType.HUMIDITY: HumidityScale,
    MultilevelSensorType.VELOCITY: VelocityScale,
    MultilevelSensorType.DIRECTION: DirectionScale,
    MultilevelSensorType.ATMOSPHERIC_PRESSURE: AirPressureScale,
    MultilevelSensorType.BAROMETRIC_PRESSURE: AirPressureScale,
    MultilevelSensorType.SOLAR_RADIATION: SolarRadiationScale,
    MultilevelSensorType.DEW_POINT: TemperatureScale,
    MultilevelSensorType.RAIN_RATE: RainRateScale,
    MultilevelSensorType.TIDE_LEVEL: TideLevelScale,
    MultilevelSensorType.WEIGHT: WeightScale,
    MultilevelSensorType.VOLTAGE: VoltageScale,
    MultilevelSensorType.CURRENT: CurrentScale,
    MultilevelSensorType.CARBON_DIOXIDE_LEVEL: CarbonDioxideLevelScale,
    MultilevelSensorType.AIR_FLOW: AirFlowScale,
    MultilevelSensorType.TANK_CAPACITY: TankCapacityScale,
    MultilevelSensorType.DISTANCE: DistanceScale,
    MultilevelSensorType.ANGLE_POSITION: AnglePositionScale,
    MultilevelSensorType.ROTATION: RotationScale,
    MultilevelSensorType.WATER_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.SOIL_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.SEISMIC_INTENSITY: SeismicIntensityScale,
    MultilevelSensorType.SEISMIC_MAGNITUDE: SeismicMagnitudeScale,
    MultilevelSensorType.ULTRAVIOLET: UltravioletScale,
    MultilevelSensorType.ELECTRICAL_RESISTIVITY: ElectricalResistivityScale,
    MultilevelSensorType.ELECTRICAL_CONDUCTIVITY: ElectricalConductivityScale,
    MultilevelSensorType.LOUDNESS: LoudnessScale,
    MultilevelSensorType.MOISTURE: MoistureScale,
    MultilevelSensorType.FREQUENCY: FrequencyScale,
    MultilevelSensorType.TIME: TimeScale,
    MultilevelSensorType.TARGET_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.PARTICULATE_MATTER_2_5: ParticulateMatter25Scale,
    MultilevelSensorType.FORMALDEHYDE_LEVEL: FormaldehydeLevelScale,
    MultilevelSensorType.RADON_CONCENTRATION: RadonConcentrationScale,
    MultilevelSensorType.METHANE_DENSITY: MethaneDensityScale,
    MultilevelSensorType.VOLATILE_ORGANIC_COMPOUND_LEVEL: VolatileOrganicCompoundLevelScale,
    MultilevelSensorType.CARBON_MONOXIDE_LEVEL: CarbonMonoxideLevelScale,
    MultilevelSensorType.SOIL_HUMIDITY: PercentageScale,
    MultilevelSensorType.SOIL_REACTIVITY: AcidityScale,
    MultilevelSensorType.SOIL_SALINITY: SoilSalinityScale,
    MultilevelSensorType.HEART_RATE: HeartRateScale,
    MultilevelSensorType.BLOOD_PRESSURE: BloodPressureScale,
    MultilevelSensorType.MUSCLE_MASS: MassScale,
    MultilevelSensorType.FAT_MASS: MassScale,
    MultilevelSensorType.BONE_MASS: MassScale,
    MultilevelSensorType.TOTAL_BODY_WATER: MassScale,
    MultilevelSensorType.BASIS_METABOLIC_RATE: BasisMetabolicRateScale,
    MultilevelSensorType.BODY_MASS_INDEX: BodyMassIndexScale,
    MultilevelSensorType.ACCELERATION_X_AXIS: AccelerationScale,
    MultilevelSensorType.ACCELERATION_Y_AXIS: AccelerationScale,
    MultilevelSensorType.ACCELERATION_Z_AXIS: AccelerationScale,
    MultilevelSensorType.SMOKE_DENSITY: PercentageScale,
    MultilevelSensorType.WATER_FLOW: WaterFlowScale,
    MultilevelSensorType.WATER_PRESSURE: WaterPressureScale,
    MultilevelSensorType.RF_SIGNAL_STRENGTH: RfSignalStrengthScale,
    MultilevelSensorType.PARTICULATE_MATTER_10: ParticulateMatter10Scale,
    MultilevelSensorType.RESPIRATORY_RATE: RespiratoryRateScale,
    MultilevelSensorType.RELATIVE_MODULATION_LEVEL: PercentageScale,
    MultilevelSensorType.BOILER_WATER_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.DOMESTIC_HOT_WATER_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.OUTSIDE_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.EXHAUST_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.WATER_CHLORINE_LEVEL: WaterChlorineLevelScale,
    MultilevelSensorType.WATER_ACIDITY: AcidityScale,
    MultilevelSensorType.WATER_OXIDATION_REDUCTION_POTENTIAL: WaterOxidationReductionPotentialScale,
    MultilevelSensorType.HEART_RATE_LF_HF_RATIO: UnitlessScale,
    MultilevelSensorType.MOTION_DIRECTION: DirectionScale,
    MultilevelSensorType.APPLIED_FORCE_ON_THE_SENSOR: AppliedForceOnTheSensorScale,
    MultilevelSensorType.RETURN_AIR_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.SUPPLY_AIR_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.CONDENSER_COIL_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.EVAPORATOR_COIL_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.LIQUID_LINE_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.DISCHARGE_LINE_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.SUCTION_PRESSURE: PressureScale,
    MultilevelSensorType.DISCHARGE_PRESSURE: PressureScale,
    MultilevelSensorType.DEFROST_TEMPERATURE: TemperatureScale,
    MultilevelSensorType.OZONE: DensityScale,
    MultilevelSensorType.SULFUR_DIOXIDE: DensityScale,
    MultilevelSensorType.NITROGEN_DIOXIDE: DensityScale,
    MultilevelSensorType.AMMONIA: DensityScale,
    MultilevelSensorType.LEAD: DensityScale,
    MultilevelSensorType.PARTICULATE_MATTER_1: DensityScale,
    MultilevelSensorType.PERSON_COUNTER_ENTERING: UnitlessScale,
    MultilevelSensorType.PERSON_COUNTER_EXITING: UnitlessScale,
}

CO_SENSORS = {MultilevelSensorType.CARBON_MONOXIDE_LEVEL}
CO2_SENSORS = {MultilevelSensorType.CARBON_DIOXIDE_LEVEL}
CURRENT_SENSORS = {MultilevelSensorType.CURRENT}
ENERGY_MEASUREMENT_SENSORS = {MultilevelSensorType.BASIS_METABOLIC_RATE}
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
