"""Naming policy command."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING
from quality.lib.output import write_error
from quality.lib.json_config import JsonConfigError
from quality.repository.naming.policy import read_policy
from quality.repository.naming.analyze import analyze_names
from quality.config.repository.paths import PYTHON_SOURCE_DIRS
from quality.shell.scope import find_shell_files, parse_scope_list
from quality.repository.naming.checks.shell import check_shell_names
from quality.lib.diagnostics import report_diagnostics, report_violations
from quality.lib.files import git_files, VISIBLE_FILE_ARGUMENTS, STAGED_FILE_ARGUMENTS
from quality.python.rules.prefix_collisions import collect_prefix_collision_violations
from quality.python.rules.single_file_folders import collect_single_package_violations
from quality.repository.naming.checks.folders import check_single_script_folders, collect_ambiguous_folder_violations
from quality.config.naming.rules import (
    SHELL_SCOPES,
    PYTHON_SCOPES,
    SCOPE_SOURCE_DIRS,
    SINGLE_FILE_SOURCE_ROOTS,
)

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


def collect_shell_naming_diagnostics(scope: str, root: Path) -> list[Diagnostic]:
    """Return shell naming diagnostics."""
    requested_paths = (
        git_files(STAGED_FILE_ARGUMENTS, root=root, is_existing_required=True) if scope == "staged" else []
    )
    files = find_shell_files(scope, requested_paths, root=root, is_shebang_included=True)
    errors: list[Diagnostic] = []
    errors.extend(check_shell_names(files))
    errors.extend(check_single_script_folders(files))
    return errors


def collect_python_diagnostics(scope: str, root: Path) -> list[Diagnostic]:
    """Return prefix and single-file-package diagnostics."""
    visible_paths = [
        path for path in git_files(VISIBLE_FILE_ARGUMENTS, root=root, is_existing_required=True) if path.endswith(".py")
    ]
    source_roots = python_source_roots(scope)
    if scope == "staged":
        staged_python = [
            Path(path)
            for path in git_files(STAGED_FILE_ARGUMENTS, root=root, is_existing_required=False)
            if path.endswith(".py")
        ]
        prefix_directories = {path.parent for path in staged_python}
        package_directories = affected_package_directories(staged_python, source_roots)
    else:
        governed = [
            path
            for path in map(Path, visible_paths)
            if any(path == root or root in path.parents for root in source_roots)
        ]
        prefix_directories = {path.parent for path in governed}
        package_directories = set(prefix_directories)

    diagnostics = collect_prefix_collision_violations(root, prefix_directories, visible_paths)
    single_file_roots = {path for path in source_roots if path.parts and path.parts[0] in SINGLE_FILE_SOURCE_ROOTS}
    single_file_directories = {
        path for path in package_directories if any(path == root or root in path.parents for root in single_file_roots)
    }
    diagnostics.extend(
        collect_single_package_violations(
            single_file_directories,
            visible_paths,
            single_file_roots,
        ),
    )
    return diagnostics


def python_source_roots(scope: str) -> set[Path]:
    """Return configured Python source roots for one scope."""
    if scope == "staged":
        return {Path(path) for path in PYTHON_SOURCE_DIRS}
    roots: set[Path] = set()
    for scope_part in parse_scope_list(scope):
        configured = SCOPE_SOURCE_DIRS.get(scope_part)
        if configured is None:
            roots.add(Path(scope_part))
        else:
            roots.update(Path(path) for path in configured)
    return roots


def affected_package_directories(paths: list[Path], source_roots: set[Path]) -> set[Path]:
    """Return package directories whose structure can change with staged paths."""
    directories: set[Path] = set()
    for path in paths:
        parent = path.parent
        for source_root in source_roots:
            if path != source_root and source_root not in path.parents:
                continue
            while parent != source_root.parent:
                directories.add(parent)
                if parent == source_root:
                    break
                parent = parent.parent
            break
    return directories


def run_naming_policy(scope: str = "all", root: str | Path = ".") -> int:
    """Run naming policy and print diagnostics."""
    root_path = Path(root).resolve()
    try:
        policy = read_policy(root_path)
    except JsonConfigError as error:
        write_error(str(error))
        return 1

    diagnostics = analyze_names(policy, scope, root_path)
    scope_parts = parse_scope_list(scope)
    if any(scope_part in PYTHON_SCOPES for scope_part in scope_parts):
        diagnostics.extend(collect_python_diagnostics(scope, root_path))
    if any(scope_part in SHELL_SCOPES for scope_part in scope_parts):
        diagnostics.extend(collect_shell_naming_diagnostics(scope, root_path))

    exit_code = report_diagnostics("Naming policy violations:", diagnostics)
    if scope == "all":
        violations = collect_ambiguous_folder_violations(root_path)
        if report_violations("Ambiguous folder name violations:", violations) != 0:
            exit_code = 1
    return exit_code


def main() -> int:
    """Run naming policy."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default="all")
    arguments = parser.parse_args()
    return run_naming_policy(arguments.scope, Path.cwd())


if __name__ == "__main__":
    raise SystemExit(main())
