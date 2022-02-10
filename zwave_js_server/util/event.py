"""Utility function for Z-Wave JS events."""
from typing import Any, Dict, List, Literal

from pydantic import ValidationError

from ..model.controller.event_model import CONTROLLER_EVENT_MODEL_MAP
from ..model.driver import DRIVER_EVENT_MODEL_MAP
from ..model.node.event_model import NODE_EVENT_MODEL_MAP

SOURCE_TO_EVENT_TO_MODEL_MAP = {
    "controller": CONTROLLER_EVENT_MODEL_MAP,
    "driver": DRIVER_EVENT_MODEL_MAP,
    "node": NODE_EVENT_MODEL_MAP,
}


def validate_event_data(
    data: Dict[str, Any],
    source: Literal["controller", "driver", "node"],
    event_name: str,
    keys_can_be_missing: bool = False,
) -> None:
    """
    Validate data with a pydantic model using event name and source.

    Raises an exception if data is invalid.
    keys_can_be_missing allows for required keys to be missing when True.
    """

    if source not in SOURCE_TO_EVENT_TO_MODEL_MAP:
        raise ValueError(f"Invalid source: {source}")
    try:
        SOURCE_TO_EVENT_TO_MODEL_MAP[source][event_name](**data)
    except ValidationError as exc:
        errors: List[Dict[str, Any]] = []
        for error in exc.errors():
            # Filter out required field errors if keys can be missing
            if error["msg"] == "field required" and keys_can_be_missing:
                continue
            errors.append(error)

        # If there are still errors after filtering, raise an exception
        if errors:
            raise ValueError(errors) from exc
    except KeyError as exc:
        raise TypeError(f"{event_name} is not a valid event name") from exc
