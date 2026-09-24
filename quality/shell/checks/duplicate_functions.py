"""Detect duplicate shell function bodies."""

from __future__ import annotations

from typing import TYPE_CHECKING
from collections import defaultdict
from quality.lib.diagnostics import diagnostic
from quality.shell.parsers import collect_shell_functions, strip_shell_comments
from quality.config.shell import SHELL_DUPLICATE_MIN_LINES, SHELL_DUPLICATE_MIN_MATCHES

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


def collect_duplicate_function_bodies(sources: dict[str, str]) -> list[Diagnostic]:
    """Return duplicate function body diagnostics."""
    bodies: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    for path, source in sources.items():
        for function in collect_shell_functions(source):
            body = "\n".join(
                strip_shell_comments(str(line)).strip()
                for line in function["body"]
                if strip_shell_comments(str(line)).strip()
            )
            if len(body.splitlines()) >= SHELL_DUPLICATE_MIN_LINES:
                bodies[body].append((path, str(function["name"]), int(function["start"])))
    errors: list[Diagnostic] = []
    for matches in bodies.values():
        if len(matches) < SHELL_DUPLICATE_MIN_MATCHES:
            continue
        names = ", ".join(f"{path}:{name}" for path, name, _ in matches)
        for path, name, line in matches:
            errors.append(
                diagnostic(
                    path,
                    line,
                    "shell.duplicate-function",
                    f"{name} duplicates function body shared by {names}",
                ),
            )
    return errors
