"""Provide tests for zwave-js-server."""
import pathlib


def load_fixture(name):
    """Load a fixture."""
    return (pathlib.Path(__file__).parent / "fixtures" / name).read_text()
