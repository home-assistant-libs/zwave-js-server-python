"""Test the node model."""
import json
from unittest.mock import call

from zwave_js_server.model import node as node_pkg

from .. import load_fixture

DEVICE_CLASS_FIXTURE = {
    "basic": "Routing Slave",
    "generic": "Static Controller",
    "specific": "PC Controller",
    "mandatory_supported_ccs": [],
    "mandatory_controlled_ccs": ["Basic"],
}

DEVICE_CONFIG_FIXTURE = {
    "manufacturer_id": 134,
    "manufacturer": "AEON Labs",
    "label": "ZW090",
    "description": "Z‐Stick Gen5 USB Controller",
    "devices": [
        {"productType": "0x0001", "productId": "0x005a"},
        {"productType": "0x0101", "productId": "0x005a"},
        {"productType": "0x0201", "productId": "0x005a"},
    ],
    "firmware_version": {"min": "0.0", "max": "255.255"},
    "associations": {},
    "param_information": {"_map": {}},
}


def test_from_state():
    """Test from_state method."""
    state = json.loads(load_fixture("basic_dump.txt").split("\n")[0])["state"]

    node = node_pkg.Node(None, state["nodes"][0])

    assert node.node_id == 1
    assert node.index == 0
    assert node.status == 4
    assert node.ready is True
    for attr, value in DEVICE_CLASS_FIXTURE.items():
        assert getattr(node.device_class, attr) == value

    assert node.is_listening is True
    assert node.is_frequent_listening is False
    assert node.is_routing is False
    assert node.max_baud_rate == 40000
    assert node.is_secure is False
    assert node.version == 4
    assert node.is_beaming is True
    assert node.manufacturer_id == 134
    assert node.product_id == 90
    assert node.product_type == 257
    for attr, value in DEVICE_CONFIG_FIXTURE.items():
        assert getattr(node.device_config, attr) == value
    assert node.label == "ZW090"
    assert node.neighbors == [31, 32, 33, 36, 37, 39, 52]
    assert node.interview_attempts == 1


async def test_set_value(ws_client, node, uuid4):
    """Test set value."""
    value_id = "52-32-00-targetValue-00"
    value = node.values[value_id]
    await node.async_set_value(value_id, 42)

    msg = {
        "command": "node.set_value",
        "nodeId": node.node_id,
        "valueId": value.data,
        "value": 42,
        "messageId": uuid4,
    }

    assert ws_client.send_json.call_args == call(msg)
