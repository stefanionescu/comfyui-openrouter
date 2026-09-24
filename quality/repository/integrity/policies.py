"""Validate registered JSON quality policies through closed schemas."""

from __future__ import annotations

from pathlib import Path
from quality.lib.output import write_error
from quality.lib.json_config import JsonConfigError
from quality.repository.naming.policy import read_policy
from quality.repository.licenses.policy import read_license_policy
from quality.repository.functions.policy import read_function_policy
from quality.python.policy import read_import_policy, read_package_policy


def main() -> int:
    """Load every registered quality policy and report all schema violations."""
    root = Path.cwd()
    errors: list[str] = []
    for name, read_registered_policy in (
        ("function", read_function_policy),
        ("imports", read_import_policy),
        ("packages", read_package_policy),
        ("licenses", read_license_policy),
        ("naming", read_policy),
    ):
        try:
            read_registered_policy(root)
        except (JsonConfigError, RuntimeError) as error:
            errors.append(f"{name}: {error}")
    if errors:
        write_error("Quality policy violations:")
        for error in errors:
            write_error(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
