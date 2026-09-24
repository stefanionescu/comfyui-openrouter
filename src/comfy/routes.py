"""Register the extension's local routes with ComfyUI."""

import folder_paths
from pathlib import Path
from comfy.cli_args import args
from server import PromptServer
from .runtime import get_runtime
from ..settings.routes import ConfigurationRoutes
from ..types.errors import ErrorCode, OpenRouterError
from ..config.messages.settings import PRIVATE_STATE_LOCATION

# The installed extension, which the private state must stay out of.
EXTENSION_ROOT = Path(__file__).resolve().parents[2]


def register_routes() -> None:
    """Reject public state locations before enabling key writes, then register every local route."""
    store = get_runtime().configuration
    directory = store.directory.resolve()
    public_roots = (
        folder_paths.base_path,
        folder_paths.get_input_directory(),
        folder_paths.get_output_directory(),
        folder_paths.get_temp_directory(),
        folder_paths.get_user_directory(),
        str(EXTENSION_ROOT),
    )
    if any(directory.is_relative_to(Path(root).resolve()) for root in public_roots):
        raise OpenRouterError(ErrorCode.CONFIGURATION, PRIVATE_STATE_LOCATION)
    ConfigurationRoutes(store, is_multi_user=args.multi_user).register(PromptServer.instance.routes)


__all__ = ["register_routes"]
