"""Require every governed Python file to belong to a typecheck project."""

from __future__ import annotations

from pathlib import Path
from quality.config.repository.paths import PYTHON_SOURCE_DIRS
from quality.lib.files import git_files, SOURCE_ROOTS, VISIBLE_FILE_ARGUMENTS
from quality.lib.diagnostics import Diagnostic, diagnostic, report_diagnostics
from quality.lib.json_config import JsonConfigError, read_json_mapping, require_string_list


def _expand_pattern(root: Path, config_path: Path, pattern: str) -> set[str]:
    """Expand one project-relative file, directory, or glob pattern."""
    absolute_pattern = (config_path.parent / pattern).resolve()
    try:
        absolute_pattern.relative_to(root)
    except ValueError as exception:
        message = f"{config_path.relative_to(root).as_posix()} pattern escapes repository: {pattern}"
        raise JsonConfigError(message) from exception

    relative_pattern = absolute_pattern.relative_to(root).as_posix()
    matches = list(root.glob(relative_pattern))
    if not matches and absolute_pattern.exists():
        matches = [absolute_pattern]
    python_files: set[Path] = set()
    for path in matches:
        if path.is_dir():
            python_files.update(item for item in path.rglob("*") if item.suffix in {".py", ".pyi"})
        elif path.is_file() and path.suffix in {".py", ".pyi"}:
            python_files.add(path)
    return {path.resolve().relative_to(root).as_posix() for path in python_files if "__pycache__" not in path.parts}


def project_python_files(root: Path, relative_config_path: str) -> set[str]:
    """Return Python files owned by one BasedPyright project."""
    resolved_root = root.resolve()
    config_path = (resolved_root / relative_config_path).resolve(strict=True)
    payload = read_json_mapping(config_path)
    if "stubPath" in payload:
        msg = "Use installed dependency types instead of a local stubPath."
        raise JsonConfigError(msg)
    includes = require_string_list(payload.get("include"), f"{relative_config_path}.include", is_nonempty=True)
    excludes = require_string_list(payload.get("exclude", []), f"{relative_config_path}.exclude", is_nonempty=True)
    included_files: set[str] = set()
    for pattern in includes:
        matches = _expand_pattern(resolved_root, config_path, pattern)
        if not matches:
            message = f"{relative_config_path}.include entry resolves to no Python files: {pattern}"
            raise JsonConfigError(message)
        included_files.update(matches)
    excluded_files = {path for pattern in excludes for path in _expand_pattern(resolved_root, config_path, pattern)}
    return included_files - excluded_files


def unassigned_python_files(root: Path) -> list[str]:
    """Return governed Python files that belong to no typecheck project."""
    governed_prefixes = tuple(f"{directory}/" for directory in PYTHON_SOURCE_DIRS)
    governed_files = {
        path
        for path in git_files((*VISIBLE_FILE_ARGUMENTS, "--", *SOURCE_ROOTS), root=root, is_existing_required=True)
        if Path(path).suffix in {".py", ".pyi"} and (path in PYTHON_SOURCE_DIRS or path.startswith(governed_prefixes))
    }
    assigned_files = project_python_files(root, "pyrightconfig.json")
    return sorted(governed_files - assigned_files)


def collect_typecheck_diagnostics(root: Path) -> list[Diagnostic]:
    """Return diagnostics for Python files without a typecheck owner."""
    if (root / "typings").exists():
        return [
            diagnostic("typings", 1, "typecheck.stubs", "Use installed dependency types; remove the local stub tree.")
        ]
    return [
        diagnostic(path, 1, "typecheck.unassigned", "Python file belongs to no BasedPyright project")
        for path in unassigned_python_files(root)
    ]


def main() -> int:
    """Run typecheck project coverage integrity."""
    try:
        diagnostics = collect_typecheck_diagnostics(Path.cwd())
    except (JsonConfigError, OSError, RuntimeError) as error:
        diagnostics = [diagnostic("pyrightconfig.json", 1, "typecheck.config", str(error))]
    return report_diagnostics("Typecheck coverage violations:", diagnostics)


if __name__ == "__main__":
    raise SystemExit(main())
