"""Validate shell ownership, visibility, and dependency boundaries."""

from __future__ import annotations

import re
import posixpath
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict
from quality.lib.diagnostics import diagnostic
from quality.config.shell import SHELL_ACTION_PREFIXES, SHELL_CONFIG_PREFIXES
from quality.shell.checks.bash import is_architecture_source, is_file_executable
from quality.shell.parsers import collect_shell_functions, shell_identifier_references

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic
    from quality.shell.parsers import ShellFunction

SOURCE_RE = re.compile(r"^\s*(?:source|\.)\s+")
SOURCE_ANNOTATION_RE = re.compile(r"^# shellcheck source=(?P<path>\S+)$")
BOUNDARY_RE = re.compile(r"^# Boundary: (?P<description>.+)$")
MIN_BOUNDARY_WORDS = 4


class FunctionOwner(TypedDict):
    """One repository shell function and its owning file."""

    path: str
    function: ShellFunction


def function_owners(sources: dict[str, str]) -> dict[str, FunctionOwner]:
    """Return unique shell function owners by function name."""
    owners: dict[str, FunctionOwner] = {}
    for path, source in sources.items():
        for function in collect_shell_functions(source):
            name = str(function["name"])
            if name == "main":
                continue
            if name not in owners:
                owners[name] = {"path": path, "function": function}
    return owners


def source_annotation_path(owner_path: str, annotation: str) -> str | None:
    """Return one normalized repository source annotation."""
    if annotation == "/dev/null":
        return None
    if annotation.startswith("/"):
        return annotation.removeprefix("/")
    if annotation.startswith(("scripts/", "quality/", ".mise/", ".githooks/")):
        return posixpath.normpath(annotation)
    owner_dir = Path(owner_path).parent.as_posix()
    return posixpath.normpath(posixpath.join(owner_dir, annotation))


def direct_source_dependencies(path: str, source: str) -> tuple[set[str], list[Diagnostic]]:
    """Return annotated direct sources and source-contract diagnostics."""
    lines = source.splitlines()
    dependencies: set[str] = set()
    errors: list[Diagnostic] = []
    for index, line in enumerate(lines):
        if SOURCE_RE.match(line) is None:
            continue
        previous = lines[index - 1].strip() if index > 0 else ""
        match = SOURCE_ANNOTATION_RE.fullmatch(previous)
        if match is None:
            errors.append(
                diagnostic(
                    path,
                    index + 1,
                    "shell.source-contract",
                    "source statements require an immediate repository path annotation",
                ),
            )
            continue
        dependency = source_annotation_path(path, match.group("path"))
        if dependency is not None:
            dependencies.add(dependency)
    return dependencies, errors


def has_boundary_header(source: str) -> bool:
    """Return whether a file declares a concrete architectural boundary."""
    for line in source.splitlines()[:8]:
        match = BOUNDARY_RE.fullmatch(line)
        if match is not None and len(match.group("description").split()) >= MIN_BOUNDARY_WORDS:
            return True
    return False


def check_function_visibility(
    path: str,
    function: ShellFunction,
    *,
    is_public_seen: bool,
    is_executable: bool,
    references: dict[str, dict[str, list[int]]],
) -> list[Diagnostic]:
    """Return visibility diagnostics for one function."""
    name = str(function["name"])
    is_private = name.startswith("_")
    external_paths = {other for other, names in references.items() if other != path and names.get(name)}
    internal_count = len(references[path].get(name, ()))
    errors: list[Diagnostic] = []
    if is_private and is_public_seen:
        errors.append(
            diagnostic(
                path,
                int(function["start"]),
                "shell.private-order",
                f"{name} must appear before public functions",
            ),
        )
    if is_private and external_paths:
        callers = ", ".join(sorted(external_paths))
        errors.append(
            diagnostic(
                path,
                int(function["start"]),
                "shell.private-call",
                f"{name} is private but called by {callers}",
            ),
        )
    if is_executable or name == "main" or is_private:
        return errors
    first_word = name.split("_", maxsplit=1)[0]
    if "_" not in name or first_word in SHELL_ACTION_PREFIXES:
        errors.append(
            diagnostic(
                path,
                int(function["start"]),
                "shell.public-namespace",
                f"{name} must begin with its family or domain namespace",
            ),
        )
    if not external_paths and internal_count > 0:
        errors.append(
            diagnostic(
                path,
                int(function["start"]),
                "shell.public-internal",
                f"{name} is file-local and must be private",
            ),
        )
    return errors


def check_visibility(
    sources: dict[str, str],
    references: dict[str, dict[str, list[int]]],
    root: Path,
) -> list[Diagnostic]:
    """Return private, public, ordering, and namespace diagnostics."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        functions = collect_shell_functions(source)
        is_public_seen = False
        is_executable = is_file_executable(root / path)
        for function in functions:
            name = str(function["name"])
            errors.extend(
                check_function_visibility(
                    path,
                    function,
                    is_public_seen=is_public_seen,
                    is_executable=is_executable,
                    references=references,
                ),
            )
            is_public_seen = is_public_seen or not name.startswith("_")
    return errors


def check_single_caller_files(
    sources: dict[str, str],
    references: dict[str, dict[str, list[int]]],
    root: Path,
) -> list[Diagnostic]:
    """Return one-function, one-caller pseudo-module diagnostics."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        if is_file_executable(root / path) or path.startswith(SHELL_CONFIG_PREFIXES):
            continue
        functions = collect_shell_functions(source)
        if len(functions) != 1 or has_boundary_header(source):
            continue
        function = functions[0]
        name = str(function["name"])
        callers = {other for other, names in references.items() if other != path and names.get(name)}
        if len(callers) == 1:
            errors.append(
                diagnostic(
                    path,
                    int(function["start"]),
                    "shell.single-caller-file",
                    f"{name} belongs with its sole caller {next(iter(callers))}",
                ),
            )
    return errors


def check_source_barrels(sources: dict[str, str], root: Path) -> list[Diagnostic]:
    """Return diagnostics for source-only library barrels."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        if is_file_executable(root / path) or path.startswith(SHELL_CONFIG_PREFIXES):
            continue
        source_count = sum(1 for line in source.splitlines() if SOURCE_RE.match(line))
        if source_count > 0 and not collect_shell_functions(source):
            errors.append(
                diagnostic(
                    path,
                    1,
                    "shell.source-barrel",
                    "sourced libraries must own behavior instead of re-exporting other files",
                ),
            )
    return errors


def check_direct_dependencies(
    root: Path,
    sources: dict[str, str],
    owners: dict[str, FunctionOwner],
    references: dict[str, dict[str, list[int]]],
) -> list[Diagnostic]:
    """Return diagnostics for calls that rely on transitive source order."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        dependencies, source_errors = direct_source_dependencies(path, source)
        errors.extend(source_errors)
        errors.extend(
            diagnostic(dependency, 1, "shell.library-mode", "Sourced libraries must not be executable.")
            for dependency in dependencies
            if dependency in sources and is_file_executable(root / dependency)
        )
        for name, lines in references[path].items():
            owner = owners.get(name)
            if owner is None or owner["path"] == path:
                continue
            if owner["path"] in dependencies:
                continue
            errors.append(
                diagnostic(
                    path,
                    lines[0],
                    "shell.implicit-dependency",
                    f"{name} requires a direct source of {owner['path']}",
                ),
            )
    return errors


def check_shell_architecture(sources: dict[str, str], root: Path) -> list[Diagnostic]:
    """Return all shell module architecture diagnostics."""
    governed = {path: source for path, source in sources.items() if is_architecture_source(path)}
    references = {path: shell_identifier_references(source) for path, source in governed.items()}
    owners = function_owners(governed)
    errors: list[Diagnostic] = []
    errors.extend(check_visibility(governed, references, root))
    errors.extend(check_single_caller_files(governed, references, root))
    errors.extend(check_source_barrels(governed, root))
    errors.extend(check_direct_dependencies(root, governed, owners, references))
    return errors
