"""Read JSON request bodies within local size and time limits."""

import asyncio
from aiohttp import web
from ..state import Json
from ..serialization import parse_json, mapping_value
from ..config.messages.requests import JSON_SIZE, JSON_TYPE, JSON_SYNTAX, REQUEST_TIMEOUT
from ..config.settings import MAX_SETTINGS_BYTES, REQUEST_CHUNK_BYTES, SETTINGS_TIMEOUT_SECONDS


async def read_document(request: web.Request, *, max_bytes: int = MAX_SETTINGS_BYTES) -> dict[str, Json]:
    """Read a size-limited JSON body, including without Content-Length."""
    if request.content_type != "application/json":
        raise web.HTTPUnsupportedMediaType(text=JSON_TYPE)
    if request.content_length is not None and request.content_length > max_bytes:
        raise web.HTTPRequestEntityTooLarge(max_size=max_bytes, actual_size=request.content_length, text=JSON_SIZE)
    content = bytearray()
    try:
        async with asyncio.timeout(SETTINGS_TIMEOUT_SECONDS):
            async for chunk in request.content.iter_chunked(REQUEST_CHUNK_BYTES):
                content.extend(chunk)
                if len(content) > max_bytes:
                    raise web.HTTPRequestEntityTooLarge(max_size=max_bytes, actual_size=len(content), text=JSON_SIZE)
    except TimeoutError:
        raise web.HTTPRequestTimeout(text=REQUEST_TIMEOUT) from None
    try:
        return mapping_value(parse_json(content.decode("utf-8"), max_bytes=max_bytes))
    except UnicodeError:
        raise web.HTTPBadRequest(text=JSON_SYNTAX) from None


__all__ = ["read_document"]
