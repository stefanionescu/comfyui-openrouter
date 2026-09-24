"""Register the extension's nodes and local routes with ComfyUI."""

import asyncio
from .nodes import NODE_TYPES
from .runtime import initialize_runtime
from .comfy.routes import register_routes
from comfy_api.latest import io, ComfyExtension


class OpenRouterExtension(ComfyExtension):
    """Own the extension's host registration."""

    async def on_load(self) -> None:
        """Create the shared stores off the event loop, then register the local routes."""
        await asyncio.to_thread(initialize_runtime)
        register_routes()

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        """Return the node classes in menu order."""
        return list(NODE_TYPES)


__all__ = ["OpenRouterExtension"]
