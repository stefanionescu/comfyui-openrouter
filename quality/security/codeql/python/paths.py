"""Validate CodeQL config paths."""

from __future__ import annotations

from pathlib import Path
from quality.lib.files import read_utf8
from quality.lib.output import write_error


def main() -> int:
    """Validate CodeQL path entries exist."""
    config_path = Path("quality/config/security/codeql/python/scan.yml")
    paths = codeql_paths(read_utf8(config_path))
    violations = [path for path in paths if not Path(path).exists()]
    if not violations:
        return 0
    write_error("CodeQL path violations:")
    for violation in violations:
        write_error(f"- {violation}")
    return 1


def codeql_paths(source_text: str) -> list[str]:
    """Return path entries from the CodeQL YAML config."""
    paths: list[str] = []
    is_in_paths = False
    for line in source_text.splitlines():
        if line.startswith("paths:"):
            is_in_paths = True
            continue
        if is_in_paths and line and not line.startswith(" "):
            break
        if is_in_paths:
            stripped = line.strip()
            if stripped.startswith("- "):
                paths.append(stripped[2:].strip())
    return paths


if __name__ == "__main__":
    raise SystemExit(main())
