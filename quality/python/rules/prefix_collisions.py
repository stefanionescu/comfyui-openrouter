"""Detect prefix collisions among Python siblings."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from collections import defaultdict
from quality.lib.diagnostics import diagnostic
from quality.config.python.limits import PREFIXED_FILES_THRESHOLD
from quality.config.repository.folders import PYTHON_PREFIX_COLLISION_ALLOWLIST

if TYPE_CHECKING:
    from collections.abc import Iterable
    from quality.lib.diagnostics import Diagnostic


def filename_prefix(filename: str) -> str | None:
    """Return the first underscore-delimited filename segment; a one-word name is its own prefix."""
    stem = Path(filename).stem
    if stem.startswith(("test_", "_")):
        return None
    return stem.split("_")[0]


def python_siblings(python_paths: Iterable[str]) -> dict[Path, list[str]]:
    """Return governed Python filenames grouped by parent directory."""
    siblings: dict[Path, list[str]] = defaultdict(list)
    for relative_path in python_paths:
        path = Path(relative_path)
        if path.suffix == ".py" and path.name != "__init__.py":
            siblings[path.parent].append(path.name)
    return siblings


def collision_groups(filenames: list[str]) -> dict[str, list[str]]:
    """Return governed filename groups keyed by shared prefix."""
    groups: dict[str, list[str]] = defaultdict(list)
    for filename in filenames:
        prefix = filename_prefix(filename)
        if prefix is not None:
            groups[prefix].append(filename)
    return groups


def collect_prefix_collision_violations(
    root: Path,
    directories: Iterable[Path],
    python_paths: Iterable[str],
) -> list[Diagnostic]:
    """Return prefix collisions in selected directories using visible siblings."""
    allowed = {Path(path) for path in PYTHON_PREFIX_COLLISION_ALLOWLIST}
    siblings = python_siblings(python_paths)
    violations: list[Diagnostic] = []
    for directory in sorted(set(directories)):
        if directory in allowed:
            continue
        filenames = siblings.get(directory, [])
        if len(filenames) < PREFIXED_FILES_THRESHOLD:
            continue
        for prefix, matches in sorted(collision_groups(filenames).items()):
            if len(matches) < PREFIXED_FILES_THRESHOLD:
                continue
            display_path = directory.as_posix()
            violations.append(
                diagnostic(
                    display_path if display_path != "." else root.name,
                    1,
                    "python.prefix-collision",
                    f"prefix {prefix!r} is shared by {', '.join(sorted(matches))}",
                ),
            )
    return violations
