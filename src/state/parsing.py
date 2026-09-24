"""Parse JSON within size and depth limits, refusing duplicate keys and values JSON cannot hold."""

import json
import math
from . import Json
from typing import cast
from ..errors import ErrorCode, ConnectorError
from ..config.security import MAX_JSON_BYTES, MAX_JSON_DEPTH
from ..config.messages.requests import JSON_SIZE, JSON_DEPTH, JSON_MAPPING, JSON_SYNTAX, JSON_VALUES, JSON_DUPLICATE_KEY


def parse_json(text: str, *, max_bytes: int = MAX_JSON_BYTES, max_depth: int = MAX_JSON_DEPTH) -> Json:
    """Reject oversized, nested, duplicate-key, and non-finite JSON input."""
    if len(text.encode("utf-8")) > max_bytes:
        raise ConnectorError(ErrorCode.INVALID_INPUT, JSON_SIZE)
    try:
        value = cast("object", json.loads(text, object_pairs_hook=_unique_fields))
        return _validate_json(value, max_depth=max_depth)
    except (ValueError, RecursionError) as error:
        raise ConnectorError(ErrorCode.INVALID_INPUT, JSON_SYNTAX) from error


def _unique_fields(pairs: list[tuple[str, Json]]) -> dict[str, Json]:
    """Build a JSON object while rejecting duplicate keys."""
    result: dict[str, Json] = {}
    for key, value in pairs:
        if key in result:
            msg = JSON_DUPLICATE_KEY
            raise ValueError(msg)
        result[key] = value
    return result


def _validate_json(value: object, *, max_depth: int = MAX_JSON_DEPTH) -> Json:
    """Copy JSON values within the nesting limit; reject other Python objects."""
    if max_depth < 0:
        raise ConnectorError(ErrorCode.INVALID_INPUT, JSON_DEPTH)
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, list):
        items = cast("list[object]", value)
        return [_validate_json(item, max_depth=max_depth - 1) for item in items]
    if isinstance(value, dict):
        entries = cast("dict[object, object]", value)
        if all(isinstance(key, str) for key in entries):
            return {cast("str", key): _validate_json(item, max_depth=max_depth - 1) for key, item in entries.items()}
    raise ConnectorError(ErrorCode.INVALID_INPUT, JSON_VALUES)


def mapping_value(value: Json) -> dict[str, Json]:
    """Require an object at a public JSON boundary."""
    if not isinstance(value, dict):
        raise ConnectorError(ErrorCode.INVALID_INPUT, JSON_MAPPING)
    return value


__all__ = ["mapping_value", "parse_json"]
