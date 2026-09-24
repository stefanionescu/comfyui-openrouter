"""Run repository function policy checks."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING
from quality.lib.languages import source_language
from quality.lib.source import read_python_source
from quality.lib.diagnostics import report_diagnostics
from quality.repository.functions.references import index_modules
from quality.repository.functions.names import list_name_violations
from quality.repository.functions.policy import read_function_policy
from quality.config.repository.paths import FUNCTION_POLICY_EXCLUDED_DIRS
from quality.repository.functions.shell import collect_shell_function_violations
from quality.repository.functions.python import collect_python_function_violations
from quality.lib.files import read_utf8, git_files, SOURCE_ROOTS, VISIBLE_FILE_ARGUMENTS, STAGED_FILE_ARGUMENTS

if TYPE_CHECKING:
    from collections.abc import Iterable
    from quality.lib.diagnostics import NamedDiagnostic

type SourceRecord = tuple[str, str, str]


def collect_sources(root: Path, paths: Iterable[str]) -> list[SourceRecord]:
    """Read governed source files from explicit repository-relative paths."""
    records: list[SourceRecord] = []
    for relative_path in paths:
        path = root / relative_path
        if not path.is_file() or any(part in FUNCTION_POLICY_EXCLUDED_DIRS for part in Path(relative_path).parts):
            continue
        if path.suffix and source_language(relative_path) is None:
            continue
        source_text = read_utf8(path)
        language = source_language(relative_path, source_text)
        if language is not None:
            records.append((relative_path, source_text, language))
    return records


def reported_paths(scope: str, root: Path, all_paths: list[str]) -> set[str]:
    """Return paths whose function definitions belong to the reporting scope."""
    if scope == "staged":
        return set(git_files(STAGED_FILE_ARGUMENTS, root=root, is_existing_required=True))
    return {path for path in all_paths if path_in_scope(path, scope)}


def path_in_scope(relative_path: str, scope: str) -> bool:
    """Return whether a repository path belongs to one function-policy scope."""
    if scope in {"", "all"}:
        return True
    if scope == "python":
        return relative_path.endswith(".py")
    if scope == "shell":
        return relative_path.endswith(".sh") or relative_path.startswith((".githooks/", ".mise/tasks/"))
    return any(relative_path.startswith(f"{part.strip().rstrip('/')}/") for part in scope.split(",") if part.strip())


def analyze_functions(scope: str, root: Path) -> list[NamedDiagnostic]:
    """Return function-policy violations for the selected repository paths."""
    policy = read_function_policy(root)
    all_paths = git_files((*VISIBLE_FILE_ARGUMENTS, "--", *SOURCE_ROOTS), root=root, is_existing_required=True)
    records = collect_sources(root, all_paths)
    sources = [
        read_python_source(root, root / relative_path) for relative_path, _, language in records if language == "python"
    ]
    modules = index_modules(sources)
    selected_paths = reported_paths(scope, root, all_paths)
    source_by_path = {source.relative_path: source for source in sources}

    errors: list[NamedDiagnostic] = []
    for relative_path, source_text, language in records:
        if relative_path not in selected_paths:
            continue
        if language == "python":
            source = source_by_path[relative_path]
            errors.extend(collect_python_function_violations(source, policy["python"], modules))
        elif language == "shell":
            errors.extend(collect_shell_function_violations(relative_path, source_text, policy["shell"]))
    errors.extend(list_name_violations(sources, policy["python"], selected_paths))
    return errors


def main() -> int:
    """Run function policy checks."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default="all")
    arguments = parser.parse_args()
    errors = analyze_functions(arguments.scope, Path.cwd())
    return report_diagnostics("Function policy violations:", errors)


if __name__ == "__main__":
    raise SystemExit(main())
