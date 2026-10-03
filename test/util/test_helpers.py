"""Test helper utilities."""

from __future__ import annotations

from typing import Any

import pytest

from zwave_js_server.exceptions import UnparseableValue
from zwave_js_server.util.helpers import (
    buffer_object_to_bytes,
    is_buffer_object,
    parse_buffer,
)


@pytest.mark.parametrize(
    "data",
    [
        [],
        [0],
        [255],
        [1, 2, 3],
    ],
)
def test_is_buffer_object_accepts_byte_values(data: list[int]) -> None:
    """Test a buffer whose items are all valid bytes is recognized."""
    assert is_buffer_object({"type": "Buffer", "data": data}) is True


@pytest.mark.parametrize(
    "data",
    [
        [-1],
        [256],
        [300],
        [1114112],
        ["not-an-int"],
        [1, 2, -3],
    ],
)
def test_is_buffer_object_rejects_non_byte_values(data: list[Any]) -> None:
    """Test a buffer carrying values outside the byte range is rejected.

    A Buffer transports bytes, so an item outside 0-255 is not a valid buffer.
    Accepting them let chr() and bytes() raise bare ValueError further down,
    which callers guarding against UnparseableValue did not catch.
    """
    assert is_buffer_object({"type": "Buffer", "data": data}) is False


@pytest.mark.parametrize(
    "data",
    [
        [-1],
        [300],
        ["not-an-int"],
    ],
)
def test_parse_buffer_raises_unparseable_value(data: list[Any]) -> None:
    """Test a malformed buffer always surfaces as UnparseableValue."""
    with pytest.raises(UnparseableValue):
        parse_buffer({"type": "Buffer", "data": data})


def test_parse_buffer_round_trips_byte_values() -> None:
    """Test a valid buffer still parses to its character string."""
    assert parse_buffer({"type": "Buffer", "data": [104, 105]}) == "hi"


def test_buffer_object_to_bytes_round_trips() -> None:
    """Test a valid buffer still unwraps to bytes."""
    assert buffer_object_to_bytes({"type": "Buffer", "data": [104, 105]}) == b"hi"
