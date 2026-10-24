"""Create the shared stores when ComfyUI loads the extension."""

from dataclasses import dataclass

from ..state.errors import ErrorCode, OpenRouterError
from ..storage.files import choose_state_directory
from ..config.storage import JOB_FILES
from ..settings.store import ConfigurationStore
from ..openrouter.videos.jobs import JobStore
from ..config.messages.settings import RUNTIME_NOT_READY


@dataclass(frozen=True, slots=True)
class Runtime:
    """State shared by this extension's nodes and routes across event loops.

    Attributes:
        configuration: Private settings and key store.
        jobs: Recorded video jobs.

    """

    configuration: ConfigurationStore
    jobs: JobStore


_runtime: Runtime | None = None


def create_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime  # noqa: PLW0603 # reason: ComfyUI initializes one shared runtime during loading.
    if _runtime is None:
        # The stores keep their state under one private directory.
        configuration = ConfigurationStore(choose_state_directory())
        _runtime = Runtime(configuration, JobStore(configuration.directory / JOB_FILES['FOLDER']))


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the extension."""
    if _runtime is None:
        raise OpenRouterError(ErrorCode.CONFIGURATION, RUNTIME_NOT_READY)
    return _runtime


__all__ = ['Runtime', 'create_runtime', 'get_runtime']
