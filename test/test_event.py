"""Test event helpers."""

from zwave_js_server import event


def test_once():
    """Test once listens to event once."""
    mock = event.EventBase()
    calls = []
    mock.once("test-event", calls.append)
    mock.emit("test-event", 1)
    mock.emit("test-event", 2)
    assert len(calls) == 1
