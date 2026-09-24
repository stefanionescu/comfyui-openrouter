"""Run ShellCheck and shfmt on the same Git-visible shell scope."""

from __future__ import annotations

import sys
from pathlib import Path
from quality.lib.output import write_error
from quality.lib.process import run_command
from quality.shell.scope import find_shell_files, parse_arguments


def main() -> int:
    """Check shell diagnostics and formatting without rewriting files."""
    scope, requested_paths = parse_arguments(sys.argv[1:])
    root = Path.cwd()
    files = find_shell_files(scope, requested_paths, root=root, is_shebang_included=True)
    if not files:
        write_error(f"No shell files found in scope {scope}.")
        return 1
    commands = (
        ["shellcheck", "--rcfile", "quality/config/shellcheckrc", "--check-sourced", "--severity=style", "--", *files],
        ["shfmt", "-d", "-i", "2", "-ci", "-s", *files],
    )
    try:
        for command in commands:
            result = run_command(command)
            if result.return_code:
                return result.return_code
    except OSError:
        write_error("ShellCheck and shfmt are required. Run mise run repo:setup.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
