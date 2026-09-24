"""Validate Bash script interpreter policy."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.shell.parsers import collect_shell_functions, strip_shell_comments
from quality.config.shell import (
    BASH_SHEBANGS,
    SHELL_BASH_4_PATTERNS,
    SHELL_CONFIG_PREFIXES,
    SHELL_ARCHITECTURE_PREFIXES,
)

if TYPE_CHECKING:
    from pathlib import Path
    from quality.lib.diagnostics import Diagnostic

RUNTIME_HEADER_RE = re.compile(r"^# Runtime: Bash [0-9]+\.[0-9]+\+, (?:Linux|macOS and Linux)\.$")
DIRECTORY_ASSIGNMENT_RE = re.compile(
    r"^(?P<name>[A-Z_][A-Z0-9_]*)=.*\bcd\b.*BASH_SOURCE\[0\].*\bpwd(?: -P)?\)",
)
SOURCE_RE = re.compile(r"^(?:source|\.)\s+")
ASSIGNMENT_RE = re.compile(r"^[A-Z_][A-Z0-9_]*=")
READONLY_RE = re.compile(r"^readonly(?:\s+-[a-zA-Z]+)?\s+")
MAIN_CALL = 'main "$@"'
REQUIRED_HEADER_LINES = 4


def is_architecture_source(path: str) -> bool:
    """Return whether a shell path uses repository script architecture."""
    matches = path.startswith(SHELL_ARCHITECTURE_PREFIXES)
    if not matches:
        return False
    return path.endswith(".sh") or path.startswith((".mise/tasks/", ".githooks/"))


def is_file_executable(path: Path) -> bool:
    """Return whether a file has any executable mode bit."""
    mode = path.stat().st_mode
    executable_bits = mode & 0o111
    return executable_bits != 0


def function_lines(source: str) -> set[int]:
    """Return every source line owned by a shell function."""
    owned: set[int] = set()
    for function in collect_shell_functions(source):
        owned.update(range(int(function["start"]), int(function["end"]) + 1))
    return owned


def meaningful_lines(source: str) -> list[tuple[int, str]]:
    """Return non-empty, non-comment shell lines."""
    lines: list[tuple[int, str]] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        code = strip_shell_comments(line).strip()
        if code:
            lines.append((line_number, code))
    return lines


def check_header(path: str, source: str) -> list[Diagnostic]:
    """Return file-header and runtime-contract diagnostics."""
    lines = source.splitlines()
    errors: list[Diagnostic] = []
    if (
        len(lines) < REQUIRED_HEADER_LINES
        or lines[1] != "#"
        or not lines[2].startswith("# ")
        or not lines[2][2:].strip()
    ):
        errors.append(
            diagnostic(
                path,
                2,
                "shell.file-header",
                "script requires a blank comment line and concrete description",
            ),
        )
    if len(lines) < REQUIRED_HEADER_LINES or not RUNTIME_HEADER_RE.fullmatch(lines[3]):
        errors.append(
            diagnostic(
                path,
                4,
                "shell.runtime-header",
                "script must declare Bash version and supported platform",
            ),
        )
    return errors


def check_directory_constants(path: str, source: str) -> list[Diagnostic]:
    """Return diagnostics for unsafe computed directory constants."""
    lines = source.splitlines()
    errors: list[Diagnostic] = []
    for line_number, line in enumerate(lines, start=1):
        code = strip_shell_comments(line).strip()
        match = DIRECTORY_ASSIGNMENT_RE.match(code)
        if match is None:
            continue
        if "CDPATH=" not in code or "cd --" not in code or "pwd -P" not in code or "||" not in code:
            errors.append(
                diagnostic(
                    path,
                    line_number,
                    "shell.directory-resolution",
                    "computed directories require CDPATH, cd --, pwd -P, and an explicit failure path",
                ),
            )
    return errors


def check_library_line(path: str, line_number: int, code: str) -> list[Diagnostic]:
    """Return diagnostics for one top-level library line."""
    errors: list[Diagnostic] = []
    is_declaration = (
        not code
        or code.startswith("#!")
        or code == "#"
        or SOURCE_RE.match(code) is not None
        or READONLY_RE.match(code) is not None
        or DIRECTORY_ASSIGNMENT_RE.match(code) is not None
    )
    if code.startswith("set "):
        errors.append(
            diagnostic(
                path,
                line_number,
                "shell.library-options",
                "sourced libraries must not change shell options",
            ),
        )
    elif re.search(r"\bexit(?:\s|$)", code):
        errors.append(
            diagnostic(path, line_number, "shell.library-exit", "sourced libraries must not call exit"),
        )
    elif code == MAIN_CALL:
        errors.append(
            diagnostic(path, line_number, "shell.library-main", "sourced libraries must not invoke main"),
        )
    elif not is_declaration and not path.startswith(SHELL_CONFIG_PREFIXES):
        errors.append(
            diagnostic(
                path,
                line_number,
                "shell.library-flow",
                "sourced libraries may not execute workflow logic while loading",
            ),
        )
    return errors


def check_library_structure(path: str, source: str) -> list[Diagnostic]:
    """Return sourced-library invocation and side-effect diagnostics."""
    functions = collect_shell_functions(source)
    owned_lines = function_lines(source)
    errors: list[Diagnostic] = []
    if any(str(function["name"]) == "main" for function in functions):
        errors.append(diagnostic(path, 1, "shell.library-main", "sourced libraries must not define main"))
    for line_number, code in meaningful_lines(source):
        if line_number in owned_lines:
            continue
        errors.extend(check_library_line(path, line_number, code))
    for line_number, code in meaningful_lines(source):
        if line_number in owned_lines and code.startswith("set "):
            errors.append(
                diagnostic(
                    path,
                    line_number,
                    "shell.library-options",
                    "sourced libraries must capture status without changing caller options",
                ),
            )
    return errors


def check_entrypoint_structure(path: str, source: str) -> list[Diagnostic]:
    """Return executable entrypoint structure diagnostics."""
    functions = collect_shell_functions(source)
    errors: list[Diagnostic] = []
    main_functions = [function for function in functions if str(function["name"]) == "main"]
    if len(main_functions) != 1:
        errors.append(
            diagnostic(
                path,
                1,
                "shell.entrypoint-main",
                "executable scripts require exactly one main function",
            ),
        )
    for function in functions:
        name = str(function["name"])
        if name != "main" and not name.startswith("_"):
            errors.append(
                diagnostic(
                    path,
                    int(function["start"]),
                    "shell.entrypoint-public",
                    f"{name} must be private because executable scripts expose only main",
                ),
            )
    significant = meaningful_lines(source)
    if not significant or significant[-1][1] != MAIN_CALL:
        errors.append(
            diagnostic(
                path,
                significant[-1][0] if significant else 1,
                "shell.entrypoint-call",
                'executable scripts must end with main "$@"',
            ),
        )
    return errors


def check_bash_compatibility(path: str, source: str) -> list[Diagnostic]:
    """Return diagnostics for syntax newer than the declared project runtime."""
    errors: list[Diagnostic] = []
    for pattern, message in SHELL_BASH_4_PATTERNS:
        compiled = re.compile(pattern)
        for line_number, line in enumerate(source.splitlines(), start=1):
            code = strip_shell_comments(line)
            if compiled.search(code):
                errors.append(diagnostic(path, line_number, "shell.bash-version", message))
    return errors


def check_bash_scripts(sources: dict[str, str], root: Path) -> list[Diagnostic]:
    """Return Bash interpreter, header, invocation, and portability diagnostics."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        lines = source.splitlines()
        if lines and lines[0] not in BASH_SHEBANGS:
            errors.append(diagnostic(path, 1, "shell.shebang", "shell scripts must use Bash"))
        if not is_architecture_source(path):
            continue
        errors.extend(check_header(path, source))
        errors.extend(check_directory_constants(path, source))
        errors.extend(check_bash_compatibility(path, source))
        if is_file_executable(root / path):
            errors.extend(check_entrypoint_structure(path, source))
        else:
            errors.extend(check_library_structure(path, source))
    return errors
