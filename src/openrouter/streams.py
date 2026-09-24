"""Read the server-sent events of a streamed OpenRouter reply."""

from __future__ import annotations

from typing import TYPE_CHECKING
from .failures import read_failure
from ..types.parsing import parse_json
from ..config.messages.media import DOWNLOAD_LIMIT
from ..config.messages.run import REPLY_UNREADABLE
from ..types.errors import ErrorCode, OpenRouterError
from ..config.openrouter import REPLY_CHUNK_BYTES, BYTES_PER_MEBIBYTE

if TYPE_CHECKING:
    import aiohttp
    from ..types import Json
    from collections.abc import AsyncIterator


async def _read_lines(response: aiohttp.ClientResponse, max_bytes: int) -> AsyncIterator[bytes]:
    """Split the reply into lines of any length, within the download limit."""
    buffer = bytearray()
    total = 0
    async for chunk in response.content.iter_chunked(REPLY_CHUNK_BYTES):
        total += len(chunk)
        if total > max_bytes:
            raise OpenRouterError(ErrorCode.MEDIA, DOWNLOAD_LIMIT.format(maximum=max_bytes // BYTES_PER_MEBIBYTE))
        buffer.extend(chunk)
        while (end := buffer.find(b"\n")) >= 0:
            yield bytes(buffer[:end])
            del buffer[: end + 1]
    if buffer:
        yield bytes(buffer)


async def read_events(response: aiohttp.ClientResponse, max_bytes: int) -> AsyncIterator[Json]:
    """Yield each data event until [DONE]; lines starting with a colon are comments, and an error event fails."""
    async for line in _read_lines(response, max_bytes):
        try:
            text = line.decode("utf-8").strip()
        except UnicodeError:
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        if not text.startswith("data:"):
            continue
        payload = text.removeprefix("data:").strip()
        if payload == "[DONE]":
            return
        try:
            event = parse_json(payload, max_bytes=max_bytes)
        except OpenRouterError:
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        if isinstance(event, dict) and "error" in event:
            raise read_failure(502, payload.encode())
        yield event


__all__ = ["read_events"]
