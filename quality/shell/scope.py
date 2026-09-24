"""Source scopes for shell quality commands."""

from __future__ import annotations

import argparse
from pathlib import Path
from quality.config.shell import BASH_SHEBANGS
from quality.lib.files import git_files, VISIBLE_FILE_ARGUMENTS
from quality.config.repository.paths import QUALITY_EXCLUDED_DIRS, SHELL_SCOPE_PREFIXES, SHELL_TASK_PREFIXES


def parse_scope_list(scope: str) -> list[str]:
    """Return comma-separated scope parts."""
    parts = [part.strip() for part in scope.split(",")]
    if not parts:
        return []
    return [part for part in parts if part]


def parse_arguments(argument_values: list[str], default_scope: str = "all") -> tuple[str, list[str]]:
    """Parse scope and requested shell-quality paths."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default=default_scope)
    parser.add_argument("paths", nargs="*")
    arguments = parser.parse_args(argument_values)
    return str(arguments.scope), list(arguments.paths)


def is_path_in_scope(relative_path: str, scope: str) -> bool:
    """Return whether a repo path belongs to the active scope."""
    if scope == "staged":
        return True
    for scope_part in parse_scope_list(scope):
        prefixes = SHELL_SCOPE_PREFIXES.get(scope_part, (scope_part.rstrip("/") + "/",))
        if any(not prefix or relative_path.startswith(prefix) for prefix in prefixes):
            return True
    return False


def list_visible_shell_files(
    scope: str,
    *,
    root: Path,
    is_shebang_included: bool,
) -> list[str]:
    """Return shell files from git tracked and untracked non-ignored files."""
    candidates = git_files(VISIBLE_FILE_ARGUMENTS, root=root, is_existing_required=True)
    files: list[str] = []
    for relative_path in candidates:
        path = root / relative_path
        if (
            not path.is_file()
            or not is_path_in_scope(relative_path, scope)
            or any(part in QUALITY_EXCLUDED_DIRS for part in Path(relative_path).parent.parts)
        ):
            continue
        relative = Path(relative_path)
        is_shebang_candidate = not relative.suffix and relative_path.startswith(tuple(SHELL_TASK_PREFIXES))
        if path.suffix == ".sh" or (is_shebang_included and is_shebang_candidate and has_shell_shebang(path)):
            files.append(relative_path)
    return sorted(files)


def find_shell_files(
    scope: str,
    requested_paths: list[str],
    *,
    root: Path,
    is_shebang_included: bool,
) -> list[str]:
    """Return shell files from explicit input or tracked repository files."""
    if not requested_paths:
        return list_visible_shell_files(scope, root=root, is_shebang_included=is_shebang_included)
    files: list[str] = []
    for requested_path in requested_paths:
        relative = Path(requested_path)
        path = root / relative
        if path.is_dir():
            files.extend(
                candidate.relative_to(root).as_posix() for candidate in path.rglob("*.sh") if candidate.is_file()
            )
        elif path.is_file() and (path.suffix == ".sh" or (is_shebang_included and has_shell_shebang(path))):
            files.append(relative.as_posix())
    return sorted(files)


def has_shell_shebang(path: Path) -> bool:
    """Check a short byte prefix for a shell shebang without decoding binary assets."""
    maximum_length = max(len(shebang) for shebang in BASH_SHEBANGS) + 2
    with path.open("rb") as stream:
        first_line = stream.readline(maximum_length).rstrip(b"\r\n")
    return any(first_line == shebang.encode("ascii") for shebang in BASH_SHEBANGS)
