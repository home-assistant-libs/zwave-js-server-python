# GitHub Copilot & Claude Code Instructions

This repository is `zwave-js-server-python`, a Python client library for [zwave-js-server](https://github.com/zwave-js/zwave-js-server/). It mirrors the structure and events of Z-Wave JS 1:1 (`Driver`, `Controller`, `Node`, etc.).

## Scope

- One concern per PR. No bundling refactors, return-type changes, or renames into a feature/schema PR. Breaking changes go in their own PR.

## Schema version

- Tests and fixtures reference `MAX_SERVER_SCHEMA_VERSION` / `MIN_SERVER_SCHEMA_VERSION`. Never hardcode the number.
- Helpers that send `schemaVersion` (e.g. `dump-state`) negotiate `min(MAX_SERVER_SCHEMA_VERSION, server_max_schema_version)`. No raw `MAX_SERVER_SCHEMA_VERSION`.

## Typing

- Return annotation matches actual return value. If body returns `data["nvmId"]` (`int`), annotate `int`, not `dict`.
- No `Union` return when one type covers both known/unknown cases. Pick a type callers don't need to `isinstance`-discriminate.
- JSON keys are `str`. If model annotates `dict[int, ...]`, convert keys at construction (dict comprehension). Don't lie in the annotation.
- Public dict keyed by raw id (`int`), not model instance. Caller may not have the instance.

## Dataclasses & caching

- No mutable module-level default on dataclass field. Copy in `__post_init__` (`list(DEFAULT_X)`).
- `@cached_property` returns immutable container (`tuple`, not `list`).
- New `@cached_property` requires `update()` to invalidate it, plus regression test: populate cache → `update()` → assert new value.
- No per-call `dict(entry)` in cached/parsing methods. Use `typing.cast` or narrow with `in` check.

## Match existing patterns

Look for prior art in `zwave_js_server/model/` before inventing. Examples reviewers have flagged:

- `from_dict` classmethod parses server payload: `def from_dict(cls, data: <Type>DataType) -> Self`. Returns `Self`, not the explicit class.
- Rename unused parameters to `_param` (e.g. `event` in event handlers).

## Docstrings

- No open design questions or upstream-review references. Move to `# TODO` in body. Docstring states current behaviour.

## Tests

- All test function parameters typed. Concrete types (`Client`, `Driver`, `Controller`, `Node`), not `Any`.
- No conditions/branching in tests. Split or `pytest.mark.parametrize`.
- Duplicated test bodies → merge with `pytest.mark.parametrize`.
- Keyword arguments at call sites, unless the positional value is a variable with the same name as the parameter.
- Assert the full expected command payload, not just the return value. `mock_command` matches partially — incomplete assertion passes even when `nodeId`/`endpointIndex` drift.
