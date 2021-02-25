"""Test value model."""
from zwave_js_server.model.node import Node
from zwave_js_server.model.value import get_value_id


def test_metadata_string_check(client, node_bad_string_metadata_state):
    """Test that we handle metadata incorrectly labeled as string."""
    node = Node(client, node_bad_string_metadata_state)

    value_id = get_value_id(node, 99, "userCode", 0, 5, "5")

    assert value_id == "20-99-0-userCode-5-5"

    zwave_value = node.values[value_id]

    assert zwave_value.metadata.type == "string"
    assert zwave_value.value == {"some_key": "some_value"}
