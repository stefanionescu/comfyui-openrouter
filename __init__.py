"""Load the OpenRouter nodes through ComfyUI's extension entry point."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .src.extension import OpenRouterExtension


WEB_DIRECTORY = "./web"


async def comfy_entrypoint() -> "OpenRouterExtension":
    """Import host bindings only when ComfyUI loads the extension."""
    from .src.extension import OpenRouterExtension  # noqa: PLC0415 -- reason: ComfyUI initializes host imports during extension loading.

    return OpenRouterExtension()
