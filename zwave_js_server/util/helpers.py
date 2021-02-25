"""Generic Utility helper functions."""

import json
from ..exceptions import UnparseableValue


def is_json_string(value: str) -> bool:
    """Check if the provided string looks like json."""
    # NOTE: we do not use json.loads here as it is not strict enough
    return isinstance(value, str) and value.startswith("{") and value.endswith("}")


def parse_buffer_from_json(value: str) -> str:
    """Parse value from a buffer data type."""
    try:
        parsed_val = json.loads(value)
        if (
            "type" not in parsed_val
            or parsed_val["type"] != "Buffer"
            or "data" not in parsed_val
        ):
            raise ValueError("JSON string does not match expected schema")
        return "".join([chr(x) for x in parsed_val["data"]])
    except ValueError as err:
        raise UnparseableValue(f"Unparseable value: {value}") from err
