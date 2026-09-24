"""Shell source parsers for quality checks."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, TypedDict
from quality.lib.diagnostics import diagnostic

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


class ShellFunction(TypedDict):
    """One shell function with source extent and body lines."""

    name: str
    start: int
    end: int
    body: list[str]


FUNCTION_RE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\(\) \{$")
FUNCTION_END_RE = re.compile(r"^}$")
IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


def strip_shell_comments(line: str) -> str:
    """Remove comments while respecting shell quotes."""
    quote: str | None = None
    is_escaped = False
    for index, char in enumerate(line):
        if is_escaped:
            is_escaped = False
            continue
        if char == "\\":
            is_escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            continue
        if char == "#":
            return line[:index]
    return line


def collect_shell_functions(source: str) -> list[ShellFunction]:
    """Return shell function names, line ranges, and body lines."""
    lines = source.splitlines()
    functions: list[ShellFunction] = []
    index = 0
    while index < len(lines):
        match = FUNCTION_RE.match(lines[index])
        if not match:
            index += 1
            continue
        name = match.group("name")
        start = index + 1
        body: list[str] = []
        index += 1
        while index < len(lines):
            if FUNCTION_END_RE.match(lines[index]):
                break
            body.append(lines[index])
            index += 1
        functions.append({"name": name, "start": start, "end": index + 1, "body": body})
        index += 1
    return functions


def shell_identifier_references(source: str) -> dict[str, list[int]]:
    """Return unqualified shell identifier occurrences outside declarations."""
    declaration_lines = {int(function["start"]) for function in collect_shell_functions(source)}
    references: dict[str, list[int]] = {}
    for line_number, line in enumerate(source.splitlines(), start=1):
        if line_number in declaration_lines:
            continue
        code = strip_shell_comments(line)
        for name in IDENTIFIER_RE.findall(code):
            references.setdefault(name, []).append(line_number)
    return references


def function_for_line(functions: list[ShellFunction], line_number: int) -> ShellFunction | None:
    """Return the function containing one source line."""
    for function in functions:
        if int(function["start"]) <= line_number <= int(function["end"]):
            return function
    return None


def check_module_length_limit(file: str, source: str, max_lines: int) -> list[Diagnostic]:
    """Return shell file-length violations."""
    line_count = len(source.splitlines())
    if line_count <= max_lines:
        return []
    return [diagnostic(file, 1, "shell.file-length", f"{line_count} lines over {max_lines}")]


def check_function_length_limit(file: str, source: str, max_lines: int) -> list[Diagnostic]:
    """Return shell function-length violations."""
    violations: list[Diagnostic] = []
    for function in collect_shell_functions(source):
        body_length = len([line for line in function["body"] if strip_shell_comments(str(line)).strip()])
        if body_length > max_lines:
            violations.append(
                diagnostic(
                    file,
                    function["start"],
                    "shell.function-length",
                    f"{function['name']} has {body_length} lines over {max_lines}",
                ),
            )
    return violations
