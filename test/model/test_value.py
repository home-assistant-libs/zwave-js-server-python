"""Test value model."""
from zwave_js_server.model.node import Node
from zwave_js_server.model.value import get_value_id


def test_metadata_string_check(client, idl_101_lock_state):
    """Test that we handle metadata incorrectly labeled as string."""
    node = Node(client, idl_101_lock_state)

    value_id = get_value_id(node, 99, "userCode", 0, 3, "3")

    assert value_id == "26-99-0-userCode-3-3"

    zwave_value = node.values[value_id]

    assert zwave_value.metadata.type == "string"
    assert zwave_value.value == {"type": "Buffer", "data": [164, 14, 170, 86]}
