"""Identifier word splitting."""

from __future__ import annotations

import re

WORD_RE = re.compile(r"[A-Z]+(?=[A-Z][a-z]|\d|_|-|$)|[A-Z]?[a-z]+|\d+")


def identifier_parts(name: str) -> list[str]:
    """Split snake, kebab, and Pascal identifiers into lowercase words."""
    normalized = name.replace("-", "_")
    parts: list[str] = []
    for chunk in normalized.split("_"):
        if not chunk:
            continue
        parts.extend(match.group(0).lower() for match in WORD_RE.finditer(chunk))
    return parts
