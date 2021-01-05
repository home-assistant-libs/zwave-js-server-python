"""Provide tests for zwave-js-server."""
import pathlib


def load_fixture(name):
    return (pathlib.Path(__file__).parent / "fixtures" / name).read_text()
