"""Read JSON request bodies within local size and time limits."""

import asyncio
from aiohttp import web
from ..types import Json
from ..config.settings import SETTINGS_BODY
from ..config.security import JSON_MEDIA_TYPE
from ..types.parsing import parse_json, validate_fields
from ..config.messages.requests import JSON_SIZE, JSON_TYPE, JSON_SYNTAX, REQUEST_TIMEOUT


async def read_body(request: web.Request, *, max_bytes: int = SETTINGS_BODY["MAX_BYTES"]) -> dict[str, Json]:
    """Read a size-limited JSON body, including without Content-Length."""
    if request.content_type != JSON_MEDIA_TYPE:
        raise web.HTTPUnsupportedMediaType(text=JSON_TYPE)
    if request.content_length is not None and request.content_length > max_bytes:
        raise web.HTTPRequestEntityTooLarge(max_size=max_bytes, actual_size=request.content_length, text=JSON_SIZE)
    content = bytearray()
    try:
        async with asyncio.timeout(SETTINGS_BODY["TIMEOUT_SECONDS"]):
            async for chunk in request.content.iter_chunked(SETTINGS_BODY["CHUNK_BYTES"]):
                content.extend(chunk)
                if len(content) > max_bytes:
                    raise web.HTTPRequestEntityTooLarge(max_size=max_bytes, actual_size=len(content), text=JSON_SIZE)
    except TimeoutError:
        raise web.HTTPRequestTimeout(text=REQUEST_TIMEOUT) from None
    try:
        return validate_fields(parse_json(content.decode("utf-8"), max_bytes=max_bytes))
    except UnicodeError:
        raise web.HTTPBadRequest(text=JSON_SYNTAX) from None


__all__ = ["read_body"]
