"""Test the driver model."""
import json

from zwave_js_server.event import Event
from zwave_js_server.model import driver as driver_pkg

from .. import load_fixture


def test_from_state():
    """Test from_state method."""
    ws_msgs = load_fixture("basic_dump.txt").strip().split("\n")

    driver = driver_pkg.Driver(json.loads(ws_msgs[0])["state"])

    for msg in ws_msgs[1:]:
        msg = json.loads(msg)
        assert msg["type"] == "event"
        driver_event = Event(type=msg["event"]["event"], data=msg["event"])
        driver.receive_event(driver_event)

    assert len(driver.controller.nodes) == 8
