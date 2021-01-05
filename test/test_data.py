"""Tests for data class."""
import json
from zwave_js_server import data as data_pkg

from . import load_fixture


def test_from_state():
    """Test from_state method."""
    ws_msgs = load_fixture("basic_dump.txt").strip().split("\n")

    data = data_pkg.ZWaveData(json.loads(ws_msgs[0])["state"])

    for msg in ws_msgs[1:]:
        msg = json.loads(msg)
        assert msg["type"] == "event"
        data.receive_event(msg["event"])

    assert len(data.nodes) == 8
