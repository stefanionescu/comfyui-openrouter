"""List and read the PDF and text documents at the top of ComfyUI's input folder."""

import folder_paths
from pathlib import Path
from ..types.chat import Document
from ..config.openrouter import BYTES_PER_MEBIBYTE
from ..types.errors import ErrorCode, OpenRouterError
from ..config.generation.chat import DOCUMENT_TYPES, PDF_MEDIA_TYPE
from comfy_api_nodes.util.conversions import text_filepath_to_data_uri
from ..config.messages.inputs import DOCUMENT_KIND, DOCUMENT_SIZE, DOCUMENT_OUTSIDE, DOCUMENT_UNREADABLE


def list_documents() -> list[str]:
    """List the document files directly inside the input folder by name, as ComfyUI's own file nodes do."""
    folder = Path(folder_paths.get_input_directory())
    if not folder.is_dir():
        return []
    return sorted(path.name for path in folder.iterdir() if path.is_file() and path.suffix.lower() in DOCUMENT_TYPES)


def read_document(name: str, max_megabytes: int) -> Document:
    """Read one document: a PDF as a data URL, and a text file as UTF-8 text."""
    folder = Path(folder_paths.get_input_directory()).resolve()
    path = Path(folder_paths.get_annotated_filepath(name)).resolve()
    if not path.is_relative_to(folder) or not path.is_file():
        raise OpenRouterError(ErrorCode.INVALID_INPUT, DOCUMENT_OUTSIDE)
    media_type = DOCUMENT_TYPES.get(path.suffix.lower())
    if media_type is None:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, DOCUMENT_KIND)
    if path.stat().st_size > max_megabytes * BYTES_PER_MEBIBYTE:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, DOCUMENT_SIZE.format(maximum=max_megabytes))
    if media_type == PDF_MEDIA_TYPE:
        return Document(path.name, media_type, None, text_filepath_to_data_uri(str(path)))
    try:
        return Document(path.name, media_type, path.read_text(encoding="utf-8"), None)
    except UnicodeError:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, DOCUMENT_UNREADABLE) from None


__all__ = ["list_documents", "read_document"]
