"""Validate shell control-flow and mutable-state complexity."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.shell.checks.bash import is_architecture_source
from quality.shell.parsers import collect_shell_functions, strip_shell_comments
from quality.config.shell import (
    SHELL_MAX_FUNCTION_NESTING,
    SHELL_MAX_FUNCTION_BRANCHES,
    SHELL_MAX_MUTABLE_ASSIGNMENTS,
)

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic

CONTROL_START_RE = re.compile(r"^(?:if\b|for\b|while\b|until\b|case\b)")
CONTROL_END_RE = re.compile(r"^(?:fi\b|done\b|esac\b)")
BRANCH_RE = re.compile(r"^(?:if\b|elif\b|for\b|while\b|until\b)")
CASE_ARM_RE = re.compile(r"^(?!case\b).+\)\s*$")
ASSIGNMENT_RE = re.compile(r"(?:^|\s)(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?:\+)?=")


def function_complexity(body: list[str]) -> tuple[int, int, int]:
    """Return branch count, maximum nesting, and mutable-state score."""
    branches = 0
    nesting = 0
    max_nesting = 0
    assignments: dict[str, int] = {}
    global_assignments = 0
    for line in body:
        code = strip_shell_comments(line).strip()
        if not code:
            continue
        if CONTROL_END_RE.match(code):
            nesting = max(0, nesting - 1)
        if BRANCH_RE.match(code) or CASE_ARM_RE.match(code):
            branches += 1
        if CONTROL_START_RE.match(code):
            nesting += 1
            max_nesting = max(max_nesting, nesting)
        for match in ASSIGNMENT_RE.finditer(code):
            name = match.group("name")
            assignments[name] = assignments.get(name, 0) + 1
            if name.isupper() and not code.startswith(("local ", "readonly ")):
                global_assignments += 1
    repeated_assignments = sum(max(count - 1, 0) for count in assignments.values())
    return branches, max_nesting, repeated_assignments + global_assignments


def check_shell_complexity(sources: dict[str, str]) -> list[Diagnostic]:
    """Return branch, nesting, and mutable-state diagnostics."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        if not is_architecture_source(path):
            continue
        for function in collect_shell_functions(source):
            body = [str(line) for line in function["body"]]
            branches, nesting, mutable_assignments = function_complexity(body)
            start = int(function["start"])
            name = str(function["name"])
            if branches > SHELL_MAX_FUNCTION_BRANCHES:
                errors.append(
                    diagnostic(
                        path,
                        start,
                        "shell.branch-complexity",
                        f"{name} has {branches} branches over {SHELL_MAX_FUNCTION_BRANCHES}",
                    ),
                )
            if nesting > SHELL_MAX_FUNCTION_NESTING:
                errors.append(
                    diagnostic(
                        path,
                        start,
                        "shell.nesting",
                        f"{name} nests control flow {nesting} levels over {SHELL_MAX_FUNCTION_NESTING}",
                    ),
                )
            if mutable_assignments > SHELL_MAX_MUTABLE_ASSIGNMENTS:
                errors.append(
                    diagnostic(
                        path,
                        start,
                        "shell.mutable-state",
                        f"{name} has mutable-state score {mutable_assignments} over {SHELL_MAX_MUTABLE_ASSIGNMENTS}",
                    ),
                )
    return errors
