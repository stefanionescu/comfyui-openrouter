"""Data-driven name validation."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from quality.repository.naming.parts import identifier_parts

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


SNAKE_RE = re.compile(r"^_?[a-z][a-z0-9_]*_?$|^__[a-z0-9_]+__$")
UPPER_SNAKE_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PASCAL_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
CASE_PATTERNS = {
    "snake": SNAKE_RE,
    "upper-snake": UPPER_SNAKE_RE,
    "kebab": KEBAB_RE,
    "pascal": PASCAL_RE,
}


def matches_case(name: str, case_name: str) -> bool:
    """Return whether a name matches a configured case."""
    pattern = CASE_PATTERNS.get(case_name)
    if pattern is None:
        return False
    return bool(pattern.match(name))


def validate_name(name: str, cases: Iterable[str], policy: Mapping[str, object]) -> list[str]:
    """Return policy diagnostics for one name."""
    diagnostics: list[str] = []
    words = identifier_parts(name)
    if cases and not any(matches_case(name, case_name) for case_name in cases):
        diagnostics.append(f'uses invalid case for "{name}"')
    max_characters = policy.get("max_characters")
    if isinstance(max_characters, int) and len(name) > max_characters:
        diagnostics.append(f"has {len(name)} characters over limit {max_characters}")
    max_words = policy.get("max_words")
    if isinstance(max_words, int) and len(words) > max_words:
        diagnostics.append(f"has {len(words)} words over limit {max_words}")
    if len(words) != len(set(words)):
        diagnostics.append("contains duplicate words")
    return diagnostics
