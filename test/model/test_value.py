"""Test value model."""
from zwave_js_server.model.node import Node
from zwave_js_server.model.value import get_value_id


def test_buffer_dict(client, idl_101_lock_state):
    """Test that we handle buffer dictionary correctly."""
    node = Node(client, idl_101_lock_state)

    value_id = get_value_id(node, 99, "userCode", 0, 3, "3")

    assert value_id == "26-99-0-userCode-3-3"

    zwave_value = node.values[value_id]

    assert zwave_value.metadata.type == "string"
    assert zwave_value.value == "¤\x0eªV"


def test_unparseable_value(client, unparseable_json_string_value_state):
    """Test that we handle string value with unparseable format."""
    node = Node(client, unparseable_json_string_value_state)

    value_id = get_value_id(node, 99, "userCode", 0, 4, "4")

    assert value_id == "20-99-0-userCode-4-4"
    assert value_id not in node.values
