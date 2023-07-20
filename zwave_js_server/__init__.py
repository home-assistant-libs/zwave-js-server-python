"""Provide a package for zwave-js-server."""

import sys

# monkeypatch fromisoformat for Python 3.10 to support more formats
if sys.version_info < (3, 11):
    from backports.datetime_fromisoformat import MonkeyPatch

    MonkeyPatch.patch_fromisoformat()
