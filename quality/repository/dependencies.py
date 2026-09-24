"""Validate repository dependency ownership."""

from __future__ import annotations

import re
import shlex
import tomli
from typing import cast
from pathlib import Path
from quality.lib.output import write_error
from scripts.dependencies import build_requirements
from quality.lib.files import git_files, VISIBLE_FILE_ARGUMENTS
from quality.config.repository.dependencies import (
    LOCK_FILE,
    EXPORT_TASK,
    EXPORT_MODULE,
    RUNTIME_EXTRAS,
    UV_PIP_INSTALL,
    UV_PIP_WRAPPER,
    PROJECT_SECTION,
    EXPORT_SCAN_ROOTS,
    POLICY_FILE_NAMES,
    PACKAGE_NAME_FIELD,
    ALLOWED_UV_PIP_PATHS,
    DEV_DEPENDENCY_GROUP,
    LOCK_PACKAGE_SECTION,
    POLICY_FILE_SUFFIXES,
    PROJECT_PACKAGE_NAME,
    PROJECT_METADATA_FILE,
    ROOT_REQUIREMENTS_GLOB,
    DEPENDENCY_GROUPS_SECTION,
    POLICY_FILE_IGNORED_PARTS,
    DIRECT_PIP_INSTALL_PATTERN,
    INSTALL_COMMAND_SCAN_ROOTS,
    REQUIREMENTS_EXPORT_COMMAND,
    OPTIONAL_DEPENDENCIES_SECTION,
)

DIRECT_PIP_INSTALL = re.compile(DIRECT_PIP_INSTALL_PATTERN)


def collect_dependency_violations(root: Path) -> list[str]:
    """Return dependency policy diagnostics."""
    violations: list[str] = []
    if not (root / LOCK_FILE).exists():
        violations.append(f"{LOCK_FILE} is required")
    pyproject = root / PROJECT_METADATA_FILE
    if not pyproject.exists():
        return [*violations, f"{PROJECT_METADATA_FILE} is required"]

    project_config = read_toml(pyproject)
    project = _mapping(project_config.get(PROJECT_SECTION))
    dependencies = project.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies:
        violations.append(f"{PROJECT_METADATA_FILE} must list runtime dependencies")

    dependency_groups = _mapping(project_config.get(DEPENDENCY_GROUPS_SECTION))
    if DEV_DEPENDENCY_GROUP not in dependency_groups:
        violations.append(f"{PROJECT_METADATA_FILE} must define [{DEPENDENCY_GROUPS_SECTION}].{DEV_DEPENDENCY_GROUP}")

    unexpected_extras = set(_mapping(project.get(OPTIONAL_DEPENDENCIES_SECTION))) - set(RUNTIME_EXTRAS)
    violations.extend(f"Unexpected runtime extra: {extra}" for extra in sorted(unexpected_extras))
    violations.extend(collect_lock_violations(root))
    violations.extend(collect_lock_ownership(root))
    violations.extend(collect_requirements_violations(root))
    violations.extend(collect_export_workflow_violations(root))
    violations.extend(collect_install_command_violations(root))
    return violations


def read_toml(path: Path) -> dict[str, object]:
    """Return parsed TOML data."""
    parsed: object = tomli.loads(path.read_text(encoding="utf-8"))
    mapping = _mapping(parsed)
    if not mapping:
        return {}
    return mapping


def collect_lock_violations(root: Path) -> list[str]:
    """Return diagnostics for lockfile ownership of project dependencies."""
    lock_path = root / LOCK_FILE
    if not lock_path.exists():
        return []
    lock_config = read_toml(lock_path)
    packages = lock_config.get(LOCK_PACKAGE_SECTION)
    if not isinstance(packages, list):
        return [f"{LOCK_FILE} must contain package entries"]
    package_values = cast("list[object]", packages)
    project_packages = [
        package
        for value in package_values
        if (package := _mapping(value)) and package.get(PACKAGE_NAME_FIELD) == PROJECT_PACKAGE_NAME
    ]
    if not project_packages:
        return [f"{LOCK_FILE} must lock {PROJECT_PACKAGE_NAME} project dependencies"]
    provided = {extra for package in project_packages for extra in _mapping(package.get(OPTIONAL_DEPENDENCIES_SECTION))}
    missing = set(RUNTIME_EXTRAS) - provided
    unexpected = provided - set(RUNTIME_EXTRAS)
    return [
        *[f"{LOCK_FILE} must provide runtime extra {extra}" for extra in sorted(missing)],
        *[f"{LOCK_FILE} contains unexpected runtime extra {extra}" for extra in sorted(unexpected)],
    ]


def collect_lock_ownership(root: Path) -> list[str]:
    """Keep uv.lock and bun.lock as the only dependency locks, both at root."""
    forbidden = {
        "package-lock.json",
        "npm-shrinkwrap.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "bun.lockb",
        "Pipfile.lock",
        "poetry.lock",
    }
    violations: list[str] = []
    for name in git_files(VISIBLE_FILE_ARGUMENTS, root=root, is_existing_required=True):
        path = Path(name)
        if path.name in forbidden or (path.name in {"uv.lock", "bun.lock"} and path.parent != Path()):
            violations.append(f"{name}: keep only the root uv.lock and bun.lock")
    if not (root / "bun.lock").is_file():
        violations.append("The root bun.lock is required")
    return violations


def collect_requirements_violations(root: Path) -> list[str]:
    """Return diagnostics for committed root requirements files."""
    required = root / "requirements.txt"
    violations = [
        f"{path.name}: keep one runtime requirements.txt generated from project metadata"
        for path in root.glob(ROOT_REQUIREMENTS_GLOB)
        if path.is_file() and path != required
    ]
    if not required.is_file() or required.read_text(encoding="utf-8") != build_requirements(root):
        violations.append("Update requirements.txt with mise run repo:deps:export")
    return violations


def collect_export_workflow_violations(root: Path) -> list[str]:
    """Require the ComfyUI runtime export task and reject an unrelated lock export."""
    violations: list[str] = []
    export = root / EXPORT_TASK
    commands = (
        [shlex.split(line) for line in export.read_text(encoding="utf-8").splitlines()] if export.is_file() else []
    )
    if not any("-m" in command and command[command.index("-m") + 1 :] == [EXPORT_MODULE, "$@"] for command in commands):
        violations.append(f"{EXPORT_TASK} must generate ComfyUI runtime requirements")
    for path in iter_policy_files([root / scan_root for scan_root in EXPORT_SCAN_ROOTS]):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if REQUIREMENTS_EXPORT_COMMAND in line:
                violations.append(
                    f"{_relative(path, root)}:{line_number}: export only declared runtime requirements",
                )
    return violations


def collect_install_command_violations(root: Path) -> list[str]:
    """Return diagnostics for unsupported Python package install commands."""
    violations: list[str] = []
    for path in iter_policy_files([root / scan_root for scan_root in INSTALL_COMMAND_SCAN_ROOTS]):
        rel_path = _relative(path, root)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if _is_uv_pip_allowed(rel_path, line):
                continue
            if UV_PIP_INSTALL in line or UV_PIP_WRAPPER in line:
                violations.append(
                    f"{rel_path}:{line_number} must document special-package uv pip usage in dependency policy",
                )
            elif DIRECT_PIP_INSTALL.search(line):
                violations.append(
                    f"{rel_path}:{line_number} must use uv sync or {UV_PIP_INSTALL} instead of direct pip install",
                )
    return violations


def iter_policy_files(scopes: list[Path]) -> list[Path]:
    """Return existing text policy files under the selected scopes."""
    files: list[Path] = []
    for scope in scopes:
        if not scope.exists():
            continue
        if scope.is_file():
            files.append(scope)
            continue
        files.extend(path for path in scope.rglob("*") if path.is_file() and _is_text_policy_file(path))
    return sorted(files)


def _is_text_policy_file(path: Path) -> bool:
    """Return whether a file is relevant to dependency policy scans."""
    if any(part in POLICY_FILE_IGNORED_PARTS for part in path.parts):
        return False
    is_suffix_allowed = path.suffix in POLICY_FILE_SUFFIXES
    if is_suffix_allowed or path.name in POLICY_FILE_NAMES:
        return True
    return not path.suffix and path.read_bytes().startswith(b"#!/usr/bin/env bash")


def _is_uv_pip_allowed(rel_path: Path, line: str) -> bool:
    """Return whether a uv pip install line is an allowed special install."""
    if rel_path.as_posix() not in ALLOWED_UV_PIP_PATHS:
        return False
    is_uv_pip_used = UV_PIP_INSTALL in line
    return is_uv_pip_used or UV_PIP_WRAPPER in line


def _mapping(value: object) -> dict[str, object]:
    """Return a string-keyed mapping from parsed TOML values."""
    if not isinstance(value, dict):
        return {}
    raw = cast("dict[object, object]", value)
    return {key: item for key, item in raw.items() if isinstance(key, str)}


def _relative(path: Path, root: Path) -> Path:
    """Return a repository-relative path."""
    root_path = root
    relative_path = path.relative_to(root_path)
    if not relative_path.parts:
        return Path()
    return relative_path


def main() -> int:
    """Run dependency ownership checks."""
    root = Path.cwd()
    violations = collect_dependency_violations(root)
    if not violations:
        return 0
    write_error("Dependency policy violations:")
    for violation in violations:
        write_error(f"- {violation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
