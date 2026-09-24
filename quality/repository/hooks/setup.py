"""Configure repository hooks without replacing existing user hooks."""

from __future__ import annotations

from pathlib import Path
from quality.lib.process import run_command
from quality.lib.output import write_error, write_line

HOOKS = ("pre-commit", "commit-msg", "pre-push")


def configure_hooks(root: Path) -> None:
    """Preserve other hook owners and configure only this repository."""
    configured = run_command(["git", "config", "--get", "core.hooksPath"], is_output_captured=True)
    if configured.return_code not in (0, 1):
        msg = "Cannot read this repository's Git hook configuration."
        raise ValueError(msg)
    target = root / ".githooks"
    current = configured.stdout.decode().strip()
    if current and (root / current).resolve() != target.resolve():
        msg = "Existing Git hooks were preserved. Review their integration before setup."
        raise ValueError(msg)
    if not current:
        directory = Path(
            run_command(["git", "rev-parse", "--git-path", "hooks"], is_output_captured=True, is_failure_raised=True)
            .stdout.decode()
            .strip()
        )
        if any((root / directory / name).exists() for name in HOOKS):
            msg = "Existing Git hooks were preserved. Review their integration before setup."
            raise ValueError(msg)
    paths = [target / name for name in HOOKS]
    if any(not path.is_file() or path.is_symlink() for path in paths):
        msg = "Restore the three regular hook files before setup."
        raise ValueError(msg)
    for path in paths:
        path.chmod(path.stat().st_mode | 0o111)
    run_command(["git", "config", "--local", "core.hooksPath", ".githooks"], is_failure_raised=True)


def main() -> int:
    """Configure the local hook path after checking existing ownership."""
    try:
        root = Path(
            run_command(["git", "rev-parse", "--show-toplevel"], is_output_captured=True, is_failure_raised=True)
            .stdout.decode()
            .strip()
        )
        configure_hooks(root)
    except (OSError, ValueError, RuntimeError) as error:
        write_error(str(error) if isinstance(error, ValueError) else "Git hook setup failed.")
        return 1
    write_line("Configured this repository's three local Git hooks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
