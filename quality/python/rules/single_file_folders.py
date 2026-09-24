"""Detect single-file packages that should be modules."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from collections import defaultdict
from quality.lib.diagnostics import diagnostic
from quality.config.repository.folders import SINGLE_FILE_PACKAGE_ALLOWLIST

if TYPE_CHECKING:
    from collections.abc import Iterable
    from quality.lib.diagnostics import Diagnostic


def collect_single_package_violations(
    directories: Iterable[Path],
    python_paths: Iterable[str],
    source_roots: Iterable[Path],
) -> list[Diagnostic]:
    """Return selected packages with one module and no subpackages."""
    allowed = {Path(path) for path in SINGLE_FILE_PACKAGE_ALLOWLIST}
    roots = set(source_roots)
    files_by_parent: dict[Path, list[str]] = defaultdict(list)
    package_dirs: set[Path] = set()
    for relative_path in python_paths:
        path = Path(relative_path)
        if path.suffix != ".py":
            continue
        files_by_parent[path.parent].append(path.name)
        if path.name == "__init__.py":
            package_dirs.add(path.parent)

    violations: list[Diagnostic] = []
    for directory in sorted(set(directories)):
        if directory in roots or directory in allowed or directory not in package_dirs:
            continue
        modules = sorted(name for name in files_by_parent.get(directory, []) if name != "__init__.py")
        has_subpackage = any(candidate.parent == directory for candidate in package_dirs if candidate != directory)
        if len(modules) == 1 and not has_subpackage:
            violations.append(
                diagnostic(
                    directory.as_posix(),
                    1,
                    "python.single-file-package",
                    f"package contains only {modules[0]}; flatten it to a module",
                ),
            )
    return violations
