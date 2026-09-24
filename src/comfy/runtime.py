"""Create the shared stores when ComfyUI loads the extension."""

from ..storage.files import state_directory
from ..openrouter.videos.jobs import JobStore
from ..settings.store import ConfigurationStore
from ..types.errors import ErrorCode, OpenRouterError
from ..config.generation.videos import JOB_FOLDER_NAME
from ..config.messages.settings import RUNTIME_NOT_READY


class Runtime:
    """State shared by this extension's nodes and routes across event loops.

    Attributes:
        configuration: Private settings and key store.
        jobs: Recorded video jobs and uncertain video requests.

    """

    __slots__ = ("configuration", "jobs")

    configuration: ConfigurationStore
    jobs: JobStore

    def __init__(self) -> None:
        """Create the shared stores and place their state under one private directory."""
        self.configuration = ConfigurationStore(state_directory())
        self.jobs = JobStore(self.configuration.directory / JOB_FOLDER_NAME)


_runtime: Runtime | None = None


def initialize_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime  # noqa: PLW0603 -- reason: ComfyUI initializes one shared runtime during loading.
    if _runtime is None:
        _runtime = Runtime()


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the extension."""
    if _runtime is None:
        raise OpenRouterError(ErrorCode.CONFIGURATION, RUNTIME_NOT_READY)
    return _runtime


__all__ = ["Runtime", "get_runtime", "initialize_runtime"]
