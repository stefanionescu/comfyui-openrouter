"""Validate shell command, process, persistence, and deletion safety."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.shell.checks.bash import is_architecture_source
from quality.shell.parsers import collect_shell_functions, function_for_line, strip_shell_comments

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic

ECHO_RE = re.compile(r"(?:^|[;&|]|\bthen\b|\bdo\b)\s*echo(?:\s|$)")
BASH_COMMAND_STRING_RE = re.compile(r"\bbash\s+-[a-zA-Z]*[lc][a-zA-Z]*\b")
BROAD_PROCESS_RE = re.compile(r"\b(?:pkill\s+-f|killall)\b")
BLANKET_SUCCESS_RE = re.compile(r"\|\|\s*true(?:\s|$)")
COMMAND_STRING_RE = re.compile(r"\b(?:command_string|command_text|shell_command)\b")
DIRECT_RECURSIVE_REMOVE_RE = re.compile(r"\brm\s+(?:-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b")
UNCHECKED_CD_RE = re.compile(r"^\s*cd(?:\s|$)")
STATE_SOURCE_RE = re.compile(r"\bsource\s+.*(?:state|snapshot|last[_-]?config|\.env)")
UNOWNED_CLEANUP_RE = re.compile(
    r"(?:\$\{HOME\}/\.cache[\"}]|/root/\.cache[\" ]|/tmp/[^\s\"']*\*|/dev/shm/[^\s\"']*\*)",
)
LINE_RULES = (
    (ECHO_RE, "shell.echo", "use printf instead of echo"),
    (BASH_COMMAND_STRING_RE, "shell.bash-command-string", "bash -c and bash -lc are forbidden"),
    (BLANKET_SUCCESS_RE, "shell.blanket-success", "do not discard a command failure with || true"),
    (COMMAND_STRING_RE, "shell.command-string", "commands must remain argument arrays"),
    (STATE_SOURCE_RE, "shell.executable-state", "generated runtime state must never be sourced"),
)


def check_recursive_remove(
    path: str,
    line_number: int,
    code: str,
    source: str,
) -> list[Diagnostic]:
    """Return diagnostics for recursive removal outside its single owner."""
    if DIRECT_RECURSIVE_REMOVE_RE.search(code) is None:
        return []
    functions = collect_shell_functions(source)
    owner = function_for_line(functions, line_number)
    owner_name = str(owner["name"]) if owner is not None else ""
    if owner_name == "runtime_remove_owned_path":
        return []
    return [
        diagnostic(
            path,
            line_number,
            "shell.recursive-remove",
            "recursive deletion must use runtime_remove_owned_path",
        ),
    ]


def check_command_line(path: str, line_number: int, line: str, source: str) -> list[Diagnostic]:
    """Return safety diagnostics for one shell source line."""
    code = strip_shell_comments(line)
    errors = [
        diagnostic(path, line_number, code_name, message)
        for pattern, code_name, message in LINE_RULES
        if pattern.search(code)
    ]
    if UNCHECKED_CD_RE.match(code) and "||" not in code:
        errors.append(diagnostic(path, line_number, "shell.unchecked-cd", "cd requires an explicit failure path"))
    if BROAD_PROCESS_RE.search(code):
        errors.append(
            diagnostic(path, line_number, "shell.broad-process-match", "stop only the process owned by this command")
        )
    if UNOWNED_CLEANUP_RE.search(code):
        errors.append(diagnostic(path, line_number, "shell.unowned-cleanup", "remove only files owned by this command"))
    errors.extend(check_recursive_remove(path, line_number, code, source))
    return errors


def check_shell_safety(sources: dict[str, str]) -> list[Diagnostic]:
    """Return shell command and destructive-operation diagnostics."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        if not is_architecture_source(path):
            continue
        for line_number, line in enumerate(source.splitlines(), start=1):
            errors.extend(check_command_line(path, line_number, line, source))
    return errors
