"""Test event helpers."""
import pytest

from zwave_js_server import event
from zwave_js_server.model.node.event_model import (
    NODE_EVENT_MODEL_MAP,
    CheckLifelineHealthProgressEventModel,
)


def test_once():
    """Test once listens to event once."""
    mock = event.EventBase()
    calls = []
    mock.once("test-event", calls.append)
    mock.emit("test-event", 1)
    mock.emit("test-event", 2)
    assert len(calls) == 1


def test_validator():
    """Test validate_event_data function."""
    # Partial keys should pass validation if keys_can_be_missing is True
    # In this case we will get no model back
    assert (
        event.validate_event_data(
            {"rounds": 1},
            "node",
            "check lifeline health progress",
            NODE_EVENT_MODEL_MAP,
            True,
        )
        is None
    )

    # Full keys should pass validation, and even if keys_can_be_missing is True,
    # we should still get the model back
    data = {
        "source": "node",
        "event": "check lifeline health progress",
        "nodeId": 1,
        "rounds": 1,
        "totalRounds": 1,
        "lastRating": 1,
    }
    assert event.validate_event_data(
        data,
        "node",
        "check lifeline health progress",
        NODE_EVENT_MODEL_MAP,
        True,
    ) == CheckLifelineHealthProgressEventModel(**data)

    # Invalid value for partial keys should fail validation
    with pytest.raises(ValueError):
        assert event.validate_event_data(
            {"rounds": "fail"},
            "node",
            "check lifeline health progress",
            NODE_EVENT_MODEL_MAP,
            True,
        )

    # Invalid value for full keys should fail validation
    with pytest.raises(ValueError):
        assert event.validate_event_data(
            {
                "source": "node",
                "event": "check lifeline health progress",
                "nodeId": 1,
                "rounds": "event",
                "totalRounds": 1,
                "lastRating": 1,
            },
            "node",
            "check lifeline health progress",
            NODE_EVENT_MODEL_MAP,
        )

    # Invalid event type should fail validation
    with pytest.raises(TypeError):
        assert event.validate_event_data(
            {},
            "node",
            "this_is_not_a_real_event",
            NODE_EVENT_MODEL_MAP,
        )
