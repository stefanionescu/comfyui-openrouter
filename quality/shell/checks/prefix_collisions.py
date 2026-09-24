"""Detect prefix collisions among Bash files in the same directory."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from collections import defaultdict
from quality.lib.diagnostics import diagnostic
from quality.config.shell import BASH_PREFIX_ALLOWLIST, BASH_PREFIX_COLLISION_THRESHOLD

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic

BASH_FILENAME_SEPARATOR_RE = re.compile(r"[_-]")


def check_bash_prefix_collisions(files: list[str]) -> list[Diagnostic]:
    """Return same-directory Bash filename prefix diagnostics."""
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for file in sorted(set(files)):
        path = Path(file)
        prefix = BASH_FILENAME_SEPARATOR_RE.split(path.stem, maxsplit=1)[0]
        directory = path.parent.as_posix()
        allowed_prefixes = BASH_PREFIX_ALLOWLIST.get(directory, ())
        if prefix in allowed_prefixes:
            continue
        grouped[(directory, prefix)].append(file)

    errors: list[Diagnostic] = []
    for (_directory, prefix), matches in sorted(grouped.items()):
        if len(matches) < BASH_PREFIX_COLLISION_THRESHOLD:
            continue
        names = ", ".join(Path(match).name for match in matches)
        errors.append(
            diagnostic(
                matches[0],
                1,
                "shell.prefix-collision",
                f"prefix '{prefix}' is shared by {names}",
            ),
        )
    return errors


def check_file_directory_collisions(files: list[str]) -> list[Diagnostic]:
    """Return diagnostics for a Bash file that duplicates a sibling folder."""
    paths = [Path(file) for file in sorted(set(files))]
    errors: list[Diagnostic] = []
    for path in paths:
        candidate = path.parent / path.stem
        if any(candidate in other.parents for other in paths if other != path):
            errors.append(
                diagnostic(
                    path.as_posix(),
                    1,
                    "shell.file-directory-collision",
                    f"{path.name} duplicates the {candidate.name}/ owner",
                ),
            )
    return errors
