"""Tests for controller model."""
import json
from zwave_js_server import node as node_pkg

from . import load_fixture


def test_from_state():
    """Test from_state method."""
    state = json.loads(load_fixture("basic_dump.txt").split("\n")[0])["state"]

    node = node_pkg.Node(state["nodes"][0])

    assert node.node_id == 1
    assert node.index == 0
    assert node.status == 4
    assert node.ready is True
    assert node.device_class == {
        "basic": "Routing Slave",
        "generic": "Static Controller",
        "specific": "PC Controller",
        "mandatorySupportedCCs": [],
        "mandatoryControlCCs": ["Basic"],
    }
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
    assert node.device_config == {
        "manufacturerId": 134,
        "manufacturer": "AEON Labs",
        "label": "ZW090",
        "description": "Z‐Stick Gen5 USB Controller",
        "devices": [
            {"productType": "0x0001", "productId": "0x005a"},
            {"productType": "0x0101", "productId": "0x005a"},
            {"productType": "0x0201", "productId": "0x005a"},
        ],
        "firmwareVersion": {"min": "0.0", "max": "255.255"},
        "associations": {},
        "paramInformation": {"_map": {}},
    }
    assert node.label == "ZW090"
    assert node.neighbors == [31, 32, 33, 36, 37, 39, 52]
    assert node.interview_attempts == 1
