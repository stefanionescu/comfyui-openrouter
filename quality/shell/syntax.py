"""Run Bash syntax checks over scoped shell files."""

from __future__ import annotations

import sys
from pathlib import Path
from quality.lib.process import ProcessContext, run_command
from quality.shell.scope import find_shell_files, parse_arguments


def main() -> int:
    """Run bash -n against scoped files."""
    scope, requested_paths = parse_arguments(sys.argv[1:])
    root = Path.cwd()
    files = find_shell_files(scope, requested_paths, root=root, is_shebang_included=True)
    exit_code = 0
    for file in files:
        result = run_command(
            ["bash", "-n", file],
            is_failure_raised=False,
            context=ProcessContext(working_directory=root),
        )
        if result.return_code != 0:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
