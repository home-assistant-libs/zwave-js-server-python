"""Generic Utility helper functions."""
import base64
import json
from typing import Any, Dict, Union

from ..exceptions import UnparseableValue


def is_json_string(value: Any) -> bool:
    """Check if the provided string looks like json."""
    # NOTE: we do not use json.loads here as it is not strict enough
    return isinstance(value, str) and value.startswith("{") and value.endswith("}")


def convert_bytes_to_base64(data: bytes) -> str:
    """Convert bytes data to base64 for serialization."""
    return base64.b64encode(data).decode("ascii")


def parse_buffer(value: Union[Dict[str, Any], str]) -> str:
    """Parse value from a buffer data type."""
    if isinstance(value, dict):
        return parse_buffer_from_dict(value)

    if is_json_string(value):
        return parse_buffer_from_json(value)

    return value


def parse_buffer_from_dict(value: Dict[str, Any]) -> str:
    """Parse value dictionary from a buffer data type."""
    if value.get("type") != "Buffer" or "data" not in value:
        raise UnparseableValue(f"Unparseable value: {value}") from ValueError(
            "JSON does not match expected schema"
        )
    return "".join([chr(x) for x in value["data"]])


def parse_buffer_from_json(value: str) -> str:
    """Parse value string from a buffer data type."""
    try:
        return parse_buffer_from_dict(json.loads(value))
    except ValueError as err:
        raise UnparseableValue(f"Unparseable value: {value}") from err
