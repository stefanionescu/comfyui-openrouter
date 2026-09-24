"""Check the locked Python environment without installing packages."""

from __future__ import annotations

import json
from typing import cast
from quality.lib.output import write_error
from quality.lib.process import run_command


def check_environment() -> None:
    """Validate uv's offline report without changing the installed environment."""
    command = [
        "uv",
        "sync",
        "--frozen",
        "--group",
        "dev",
        "--dry-run",
        "--offline",
        "--output-format",
        "json",
    ]
    result = run_command(command, is_failure_raised=True, is_output_captured=True)
    payload: object = json.loads(result.stdout)
    if not isinstance(payload, dict):
        msg = "uv returned an invalid environment report."
        raise TypeError(msg)
    report = cast("dict[str, object]", payload)
    operation = report.get("sync")
    if report.get("dry_run") is not True or not isinstance(operation, dict):
        msg = "uv did not confirm a read-only environment check."
        raise ValueError(msg)
    operation_report = cast("dict[str, object]", operation)
    changes = operation_report.get("changes")
    if not isinstance(changes, list):
        msg = "uv returned an invalid package change list."
        raise TypeError(msg)
    if changes:
        msg = "The development environment is out of date. Run mise run repo:deps, then check again."
        raise ValueError(msg)


def main() -> int:
    """Report a clear failure when the locked environment cannot be verified."""
    try:
        check_environment()
    except (OSError, TypeError, ValueError, RuntimeError) as error:
        write_error(
            str(error) if isinstance(error, (TypeError, ValueError)) else "Cannot check the locked Python environment."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
