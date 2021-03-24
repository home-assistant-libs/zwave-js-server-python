"""Test value model."""
from copy import deepcopy

from zwave_js_server.const import ConfigurationValueType
from zwave_js_server.model.node import Node
from zwave_js_server.model.value import get_value_id


def test_value_size(lock_schlage_be469):
    """Test the value size property for a value."""
    node = lock_schlage_be469
    zwave_value = node.values["20-112-0-3"]
    assert zwave_value.metadata.value_size == 1


def test_buffer_dict(client, idl_101_lock_state):
    """Test that we handle buffer dictionary correctly."""
    node_data = deepcopy(idl_101_lock_state)
    node = Node(client, node_data)

    value_id = get_value_id(node, 99, "userCode", 0, 3)

    assert value_id == "26-99-0-userCode-3"

    zwave_value = node.values[value_id]

    assert zwave_value.metadata.type == "buffer"
    assert zwave_value.value == "¤\x0eªV"


def test_unparseable_value(client, unparseable_json_string_value_state):
    """Test that we handle string value with unparseable format."""
    node = Node(client, unparseable_json_string_value_state)

    value_id = get_value_id(node, 99, "userCode", 0, 4)

    assert value_id == "20-99-0-userCode-4"
    assert value_id not in node.values


def test_allow_manual_entry(client, inovelli_switch_state):
    """Test that allow_manaual_entry works correctly."""
    node = Node(client, inovelli_switch_state)

    config_values = node.get_configuration_values()
    value_id = get_value_id(node, 112, 8, 0, 255)

    zwave_value = config_values[value_id]

    assert zwave_value.configuration_value_type == ConfigurationValueType.MANUAL_ENTRY

    value_id = get_value_id(node, 112, 8, 0, 65280)
    zwave_value = config_values[value_id]

    assert zwave_value.configuration_value_type == ConfigurationValueType.ENUMERATED
