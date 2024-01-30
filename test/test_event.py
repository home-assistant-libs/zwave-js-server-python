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


def test_exception_on_emit(caplog):
    """Test exception on emit gets handled."""
    mock = event.EventBase()
    mock.on("test-event", lambda _: 1 / 0)
    mock.emit("test-event", 1)
    assert "Error handling event: test-event" in caplog.text
