"""Strict JSON boundary for repository quality tools."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast
from quality.lib.files import read_utf8
from collections.abc import Mapping, Sequence

if TYPE_CHECKING:
    from pathlib import Path


class JsonConfigError(ValueError):
    """A quality configuration file violates its closed schema."""


def read_json_mapping(path: Path) -> dict[str, object]:
    """Read one JSON object while rejecting duplicate and non-string keys."""
    try:
        payload: object = json.loads(read_utf8(path), object_pairs_hook=_unique_mapping)
    except (RuntimeError, json.JSONDecodeError, JsonConfigError) as exception:
        message = f"{path.as_posix()} is not valid quality JSON: {exception}"
        raise JsonConfigError(message) from exception
    if not isinstance(payload, dict):
        message = f"{path.as_posix()} must contain a JSON object"
        raise JsonConfigError(message)
    candidate = cast("dict[object, object]", payload)
    if any(not isinstance(key, str) for key in candidate):
        message = f"{path.as_posix()} must use string object members"
        raise JsonConfigError(message)
    return cast("dict[str, object]", candidate)


def _unique_mapping(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build an object while rejecting duplicate member names."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            message = f'duplicate member "{key}"'
            raise JsonConfigError(message)
        result[key] = value
    return result


def require_keys(
    value: Mapping[str, object],
    *,
    required: set[str],
    optional: set[str] | None = None,
    context: str,
) -> None:
    """Require an exact set of object members."""
    allowed = required | (optional or set())
    missing = sorted(required - value.keys())
    unknown = sorted(value.keys() - allowed)
    if missing or unknown:
        parts: list[str] = []
        if missing:
            parts.append(f"missing {', '.join(missing)}")
        if unknown:
            parts.append(f"unknown {', '.join(unknown)}")
        message = f"{context} has invalid members: {'; '.join(parts)}"
        raise JsonConfigError(message)


def require_mapping(value: object, context: str) -> dict[str, object]:
    """Return a string-keyed object or raise a schema error."""
    if not isinstance(value, dict):
        message = f"{context} must be an object"
        raise JsonConfigError(message)
    candidate = cast("dict[object, object]", value)
    if any(not isinstance(key, str) for key in candidate):
        message = f"{context} must use string object members"
        raise JsonConfigError(message)
    return cast("dict[str, object]", candidate)


def require_string(value: object, context: str) -> str:
    """Require a nonempty string in a repository configuration."""
    if not isinstance(value, str) or not value:
        message = f"{context} must be a nonempty string"
        raise JsonConfigError(message)
    return value


def require_string_list(value: object, context: str, *, is_nonempty: bool = False) -> list[str]:
    """Return a list containing only strings."""
    items = require_sequence(value, context)
    if any(not isinstance(item, str) or (is_nonempty and not item) for item in items):
        message = f"{context} must contain only {'non-empty ' if is_nonempty else ''}strings"
        raise JsonConfigError(message)
    return cast("list[str]", items)


def require_sequence(value: object, context: str) -> list[object]:
    """Return a JSON array or raise a schema error."""
    if not isinstance(value, Sequence) or isinstance(value, str):
        message = f"{context} must be an array"
        raise JsonConfigError(message)
    return list(cast("Sequence[object]", value))


def require_bool(value: object, context: str) -> bool:
    """Return a Boolean value or raise a schema error."""
    if not isinstance(value, bool):
        message = f"{context} must be Boolean"
        raise JsonConfigError(message)
    return value


def require_int(value: object, context: str, *, minimum: int = 0) -> int:
    """Return a bounded integer while rejecting Boolean values."""
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        message = f"{context} must be an integer of at least {minimum}"
        raise JsonConfigError(message)
    return value
