"""Attach a PDF or text file from ComfyUI's input folder to a chat request."""

from __future__ import annotations

import asyncio
import folder_paths
from pathlib import Path
from comfy_api.latest import io
from ...comfy.runtime import get_runtime
from typing import override, TYPE_CHECKING
from ...settings.store import read_settings
from ...config.messages.inputs import DOCUMENT_MISSING
from ...types.errors import ErrorCode, OpenRouterError
from ...comfy.documents import list_documents, read_document
from ...config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES

if TYPE_CHECKING:
    from ...types.chat import Document


class ChatAttachDocument(io.ComfyNode):
    """Add one file to the documents it receives, the way ComfyUI's own input-file nodes chain."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the input folder's documents when ComfyUI builds the node definitions; the R key reads it again."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Chat: Attach Document",
            category=MENUS["CHAT"],
            description="Attach a PDF or text file from ComfyUI's input folder to Chat: Ask.",
            inputs=[
                io.Combo.Input(
                    "file",
                    display_name="document",
                    options=list_documents(),
                    tooltip="A PDF, text, Markdown, CSV, or JSON file at the top of ComfyUI's input folder.",
                ),
                io.Custom(SOCKET_TYPES["DOCUMENTS"]).Input(
                    "documents",
                    optional=True,
                    tooltip="Connect another Chat: Attach Document to send several documents.",
                ),
            ],
            outputs=[io.Custom(SOCKET_TYPES["DOCUMENTS"]).Output("documents", display_name="documents")],
        )

    @classmethod
    def validate_inputs(cls, **_inputs: object) -> bool:
        """Take a file added after the node definitions were built; the run reads the folder itself."""
        return True

    @classmethod
    @override
    def fingerprint_inputs(cls, *, file: str = "", **_inputs: object) -> str:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        """Run again when the file is edited, replaced, or removed."""
        path = Path(folder_paths.get_annotated_filepath(file)) if file else None
        if path is None or not path.is_file():
            return file
        stat = path.stat()
        return f"{file}:{stat.st_mtime_ns}:{stat.st_size}"

    @classmethod
    @override
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, *, file: str = "", documents: tuple[Document, ...] = ()
    ) -> io.NodeOutput:
        """Read the file off the event loop and add it after the earlier documents."""
        if not file:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, DOCUMENT_MISSING)
        settings = await asyncio.to_thread(read_settings, get_runtime().configuration.directory)
        document = await asyncio.to_thread(read_document, file, settings.max_upload_megabytes)
        return io.NodeOutput((*documents, document))


__all__ = ["ChatAttachDocument"]
