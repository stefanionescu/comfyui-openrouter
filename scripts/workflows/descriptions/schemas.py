"""Answer schemas the example chat requests use to answer in JSON."""

from __future__ import annotations

import json


def build_numbered_schema(prefix: str, count: int) -> str:
    """Write a json_schema object for an object of numbered text fields, such as idea_1 to idea_3."""
    fields = [f'{prefix}_{number}' for number in range(1, count + 1)]
    schema = {
        'type': 'object',
        'properties': {field: {'type': 'string'} for field in fields},
        'required': fields,
        'additionalProperties': False,
    }
    return json.dumps({'name': f'{prefix}s', 'strict': True, 'schema': schema}, indent=2)


__all__ = ['build_numbered_schema']
