"""Scan Git-visible files without reading ignored private directories."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from quality.lib.output import write_error
from quality.lib.process import run_command
from quality.lib.files import git_files, VISIBLE_FILE_ARGUMENTS


def copy_public_files(root: Path, snapshot: Path) -> None:
    """Copy only existing Git-visible files and reject symbolic links at every path level."""
    for name in git_files(VISIBLE_FILE_ARGUMENTS, root=root, is_existing_required=True):
        source = root / name
        if source.is_symlink() or any(parent.is_symlink() for parent in source.parents if parent != root):
            msg = "Public source must not contain symbolic links."
            raise ValueError(msg)
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        # reason: Both paths use Git-listed relative filenames; source symbolic links are rejected above.
        # bearer:disable python_lang_path_traversal
        shutil.copyfile(source, target)


def main() -> int:
    """Copy public files into a disposable scan directory and redact all findings."""
    root = Path.cwd()
    try:
        with tempfile.TemporaryDirectory(prefix="comfyui-openrouter-secret-scan-") as directory:
            snapshot = Path(directory)
            copy_public_files(root, snapshot)
            command = [
                "gitleaks",
                "dir",
                str(snapshot),
                "--config",
                str(root / "quality/config/security/gitleaks/config.toml"),
                "--baseline-path",
                str(root / "quality/config/security/gitleaks/baseline.json"),
                "--no-banner",
                "--redact",
                "--ignore-gitleaks-allow",
            ]
            return run_command(command).return_code
    except (OSError, RuntimeError, ValueError) as error:
        write_error(str(error) if isinstance(error, ValueError) else "Cannot scan public repository files.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
