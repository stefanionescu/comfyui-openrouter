"""Private, atomic storage outside the installed package."""

import os
import sys
import tempfile
from pathlib import Path
from ..types.errors import ErrorCode, OpenRouterError
from ..config.messages.settings import STATE_FILE_SIZE, STATE_DIRECTORY_ABSOLUTE
from ..config.storage import TEMPORARY_PREFIX, STATE_FOLDER_NAMES, PRIVATE_FOLDER_MODE, ENVIRONMENT_VARIABLES


def choose_state_directory() -> Path:
    """Choose the platform's private state location without creating it."""
    override = os.environ.get(ENVIRONMENT_VARIABLES["STATE_DIRECTORY"])
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            raise OpenRouterError(ErrorCode.CONFIGURATION, STATE_DIRECTORY_ABSOLUTE)
        return path
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / STATE_FOLDER_NAMES["DEFAULT"]
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / STATE_FOLDER_NAMES["DEFAULT"]
    return Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")) / STATE_FOLDER_NAMES["XDG"]


def save_file(path: Path, content: bytes) -> None:
    """Replace one state file only after its complete private write succeeds."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=PRIVATE_FOLDER_MODE)
    descriptor, temporary = tempfile.mkstemp(prefix=TEMPORARY_PREFIX, dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        # reason: Callers use fixed or validated state file names inside the owner-configured private directory.
        # bearer:disable python_lang_path_traversal
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def read_file(path: Path, *, max_bytes: int) -> bytes:
    """Read a state file within its size limit."""
    with path.open("rb") as stream:
        content = stream.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise OpenRouterError(ErrorCode.CONFIGURATION, STATE_FILE_SIZE)
    return content


__all__ = ["choose_state_directory", "read_file", "save_file"]
