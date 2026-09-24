"""Validate configured source roots and folder-policy allowlists."""

from __future__ import annotations

from pathlib import Path
from quality.lib.output import write_error
from quality.config.repository.paths import CONFIG_SOURCE_DIRS, PYTHON_SOURCE_DIRS, SHELL_SOURCE_DIRS
from quality.config.shell import (
    BASH_PREFIX_ALLOWLIST,
    ALLOWED_SCRIPT_ROOT_FOLDERS,
    ALLOWED_SINGLE_SCRIPT_FOLDERS,
)
from quality.config.repository.folders import (
    AMBIGUOUS_FOLDER_ALLOWLIST,
    SINGLE_FILE_PACKAGE_ALLOWLIST,
    PYTHON_PREFIX_COLLISION_ALLOWLIST,
    AMBIGUOUS_FOLDER_EXCLUDED_PREFIXES,
)


def main() -> int:
    """Require every configured folder and allowlist entry to resolve."""
    root = Path.cwd()
    prefixes = {prefix.removesuffix("/") for prefix in AMBIGUOUS_FOLDER_EXCLUDED_PREFIXES}
    configured = {
        *PYTHON_PREFIX_COLLISION_ALLOWLIST,
        *BASH_PREFIX_ALLOWLIST,
        *SINGLE_FILE_PACKAGE_ALLOWLIST,
        *AMBIGUOUS_FOLDER_ALLOWLIST,
        *prefixes,
        *CONFIG_SOURCE_DIRS,
        *SHELL_SOURCE_DIRS,
        *ALLOWED_SCRIPT_ROOT_FOLDERS,
        *ALLOWED_SINGLE_SCRIPT_FOLDERS,
    }
    violations = [path for path in configured if path and not (root / path).is_dir()]
    for name in PYTHON_SOURCE_DIRS:
        source = root / name
        if not source.is_dir() and not (source.suffix == ".py" and source.is_file()):
            violations.append(name)
    violations.sort()
    if not violations:
        return 0
    write_error("Folder policy violations:")
    for violation in violations:
        write_error(f"- {violation} does not exist")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
