"""Test value model."""

from copy import deepcopy

from zwave_js_server.const import ConfigurationValueType, SetValueStatus
from zwave_js_server.model.node import Node
from zwave_js_server.model.value import (
    ConfigurationValue,
    ConfigurationValueFormat,
    MetaDataType,
    SetValueResult,
    ValueDataType,
    get_value_id_str,
)


def test_value_size(lock_schlage_be469):
    """Test the value size property for a value."""
    node = lock_schlage_be469
    zwave_value = node.values["20-112-0-3"]
    assert zwave_value.metadata.value_size == 1


def test_buffer_dict(client, idl_101_lock_state):
    """Test that we handle buffer dictionary correctly."""
    node_data = deepcopy(idl_101_lock_state)
    node = Node(client, node_data)

    value_id = get_value_id_str(node, 99, "userCode", 0, 3)

    assert value_id == "26-99-0-userCode-3"

    zwave_value = node.values[value_id]

    assert zwave_value.metadata.type == "buffer"
    assert zwave_value.value == "¤\x0eªV"


def test_unparseable_value(client, unparseable_json_string_value_state):
    """Test that we handle string value with unparseable format."""
    node = Node(client, unparseable_json_string_value_state)

    value_id = get_value_id_str(node, 99, "userCode", 0, 4)

    assert value_id == "20-99-0-userCode-4"
    assert value_id not in node.values


def test_allow_manual_entry(client, inovelli_switch_state):
    """Test that allow_manaual_entry works correctly."""
    node = Node(client, inovelli_switch_state)

    config_values = node.get_configuration_values()
    value_id = get_value_id_str(node, 112, 8, 0, 255)

    zwave_value = config_values[value_id]

    assert zwave_value.configuration_value_type == ConfigurationValueType.MANUAL_ENTRY

    value_id = get_value_id_str(node, 112, 8, 0, 65280)
    zwave_value = config_values[value_id]

    assert zwave_value.configuration_value_type == ConfigurationValueType.ENUMERATED


def test_stateful(lock_schlage_be469):
    """Test the stateful property for a value."""
    node = lock_schlage_be469
    zwave_value = node.values["20-112-0-3"]
    assert not zwave_value.metadata.secret


def test_secret(lock_schlage_be469):
    """Test the secret property for a value."""
    node = lock_schlage_be469
    zwave_value = node.values["20-112-0-3"]
    assert zwave_value.metadata.stateful


def test_configuration_value_type(inovelli_switch_state):
    """Test configuration value types."""
    value = ConfigurationValue(
        inovelli_switch_state,
        ValueDataType(
            commandClass=112,
            property=8,
            propertyName="8",
            endpoint=0,
            metadata=MetaDataType(
                type="boolean",
                max=2,
                min=0,
                allowManualEntry=True,
                states={True: "On", False: "Off"},
            ),
        ),
    )
    assert value.configuration_value_type == ConfigurationValueType.MANUAL_ENTRY

    value = ConfigurationValue(
        inovelli_switch_state,
        ValueDataType(
            commandClass=112,
            property=8,
            propertyName="8",
            endpoint=0,
            metadata=MetaDataType(
                type="boolean",
                max=1,
                min=0,
                allowManualEntry=False,
                states={True: "On", False: "Off"},
            ),
        ),
    )
    assert value.configuration_value_type == ConfigurationValueType.ENUMERATED

    value = ConfigurationValue(
        inovelli_switch_state,
        ValueDataType(
            commandClass=112,
            property=8,
            propertyName="8",
            endpoint=0,
            metadata=MetaDataType(
                type="boolean",
                max=1,
                min=0,
                allowManualEntry=False,
            ),
        ),
    )
    assert value.configuration_value_type == ConfigurationValueType.BOOLEAN

    value = ConfigurationValue(
        inovelli_switch_state,
        ValueDataType(
            commandClass=112,
            property=8,
            propertyName="8",
            endpoint=0,
            metadata=MetaDataType(
                type="number",
                max=2,
                min=0,
                allowManualEntry=True,
                states={0: "On", 1: "Off"},
            ),
        ),
    )
    assert value.configuration_value_type == ConfigurationValueType.MANUAL_ENTRY

    value = ConfigurationValue(
        inovelli_switch_state,
        ValueDataType(
            commandClass=112,
            property=8,
            propertyName="8",
            endpoint=0,
            metadata=MetaDataType(
                type="number",
                max=1,
                min=0,
                allowManualEntry=False,
                states={"1": "On", "0": "Off"},
            ),
        ),
    )
    assert value.configuration_value_type == ConfigurationValueType.ENUMERATED

    value = ConfigurationValue(
        inovelli_switch_state,
        ValueDataType(
            commandClass=112,
            property=8,
            propertyName="8",
            endpoint=0,
            metadata=MetaDataType(
                type="number",
                max=2,
                min=0,
                allowManualEntry=False,
            ),
        ),
    )
    assert value.configuration_value_type == ConfigurationValueType.RANGE

    value = ConfigurationValue(
        inovelli_switch_state,
        ValueDataType(
            commandClass=112,
            property=8,
            propertyName="8",
            endpoint=0,
            metadata=MetaDataType(
                type="number",
                allowManualEntry=False,
            ),
        ),
    )
    assert value.configuration_value_type == ConfigurationValueType.UNDEFINED


def test_set_value_result_str():
    """Test SetValueResult str."""
    result = SetValueResult({"status": 255})
    assert result.status == SetValueStatus.SUCCESS
    assert str(result) == "Success"

    result = SetValueResult({"status": 1, "remainingDuration": {"unit": "default"}})
    assert result.status == SetValueStatus.WORKING
    assert str(result) == "Working (default duration)"

    result = SetValueResult(
        {"status": 1, "remainingDuration": {"unit": "seconds", "value": 1}}
    )
    assert result.status == SetValueStatus.WORKING
    assert str(result) == "Working (1 seconds)"

    result = SetValueResult({"status": 3, "message": "test"})
    assert result.status == SetValueStatus.ENDPOINT_NOT_FOUND
    assert str(result) == "Endpoint Not Found: test"

    result = SetValueResult({"status": 1, "remainingDuration": "unknown"})
    assert result.status == SetValueStatus.WORKING
    assert str(result) == "Working (unknown duration)"


def test_configuration_value_metadata(inovelli_switch_state):
    """Test configuration value specific metadata."""
    value = ConfigurationValue(
        inovelli_switch_state,
        ValueDataType(
            commandClass=112,
            property=8,
            propertyName="8",
            endpoint=0,
            metadata=MetaDataType(
                type="boolean",
                max=2,
                min=0,
                allowManualEntry=True,
                states={True: "On", False: "Off"},
            ),
        ),
    )
    metadata = value.metadata
    assert metadata.default is None
    assert metadata.is_advanced is None
    assert metadata.is_from_config is None
    assert metadata.requires_re_inclusion is None
    assert metadata.no_bulk_support is None
    assert metadata.value_size is None
    assert metadata.format is None
    assert metadata.allowed is None
    assert metadata.purpose is None

    value = ConfigurationValue(
        inovelli_switch_state,
        ValueDataType(
            commandClass=112,
            property=8,
            propertyName="8",
            endpoint=0,
            metadata=MetaDataType(
                type="boolean",
                max=2,
                min=0,
                allowManualEntry=True,
                states={True: "On", False: "Off"},
                default=2,
                isAdvanced=True,
                isFromConfig=True,
                requiresReInclusion=True,
                noBulkSupport=True,
                valueSize=1,
                format=0,
                allowed=[{"value": 0}, {"from": 5, "to": 10, "step": 1}],
                purpose="state_after_power_failure",
            ),
        ),
    )
    metadata = value.metadata
    assert metadata.default == 2
    assert metadata.is_advanced
    assert metadata.is_from_config
    assert metadata.requires_re_inclusion
    assert metadata.no_bulk_support
    assert metadata.value_size == 1
    assert metadata.format == ConfigurationValueFormat.SIGNED_INTEGER
    assert metadata.allowed == [{"value": 0}, {"from": 5, "to": 10, "step": 1}]
    assert metadata.purpose == "state_after_power_failure"
