"""Send every request that carries the OpenRouter key, the only outbound code that does.

A paid request is never sent twice. Only requests that bill nothing, status checks and downloads, are
retried, because a paid request may have reached OpenRouter before its connection failed.
"""

from __future__ import annotations

import aiohttp
import asyncio
from http import HTTPStatus
from .streams import read_events
from typing import TYPE_CHECKING
from .failures import read_failure
from ..types.audio import AudioReply
from pydantic import ValidationError
from ..types.parsing import parse_json
from contextlib import asynccontextmanager
from ..config.units import BYTES_PER_MEBIBYTE
from ..config.messages.media import DOWNLOAD_LIMIT
from ..types.errors import ErrorCode, OpenRouterError
from ..config.messages.videos import VIDEO_URL_UNEXPECTED
from ..config.messages.run import REQUEST_TIMEOUT, REPLY_UNREADABLE, REQUEST_UNCERTAIN, OPENROUTER_UNREACHABLE
from ..config.openrouter import (
    GET_ATTEMPTS,
    RETRY_STATUSES,
    ATTRIBUTION_URL,
    MAX_ERROR_BYTES,
    ATTRIBUTION_TITLE,
    MAX_RETRY_SECONDS,
    MIN_RETRY_SECONDS,
    REPLY_CHUNK_BYTES,
    VIDEO_CONTENT_PREFIX,
    ATTRIBUTION_CATEGORIES,
)

if TYPE_CHECKING:
    from ..types import Json, Reply
    from ..types.settings import Configuration
    from collections.abc import Mapping, AsyncIterator, AsyncGenerator


def _create_session(configuration: Configuration, *, is_authorized: bool = True) -> aiohttp.ClientSession:
    """Open one session for one request; the key goes only to OpenRouter, never to a provider's own host.

    Proxy settings from the environment and cookies are ignored, and every request refuses redirects, so
    neither the key nor a reply can pass through another host.
    """
    headers = {
        "HTTP-Referer": ATTRIBUTION_URL,
        "X-OpenRouter-Title": ATTRIBUTION_TITLE,
        "X-OpenRouter-Categories": ATTRIBUTION_CATEGORIES,
    }
    if is_authorized:
        headers["Authorization"] = f"Bearer {configuration.credential.reveal()}"
    return aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=configuration.settings.request_timeout_seconds),
        trust_env=False,
        cookie_jar=aiohttp.DummyCookieJar(),
        headers=headers,
    )


async def _read_body(response: aiohttp.ClientResponse, configuration: Configuration) -> bytes:
    """Read a reply within the maximum download size."""
    maximum = configuration.settings.max_download_megabytes
    content = bytearray()
    async for chunk in response.content.iter_chunked(REPLY_CHUNK_BYTES):
        content.extend(chunk)
        if len(content) > maximum * BYTES_PER_MEBIBYTE:
            raise OpenRouterError(ErrorCode.MEDIA, DOWNLOAD_LIMIT.format(maximum=maximum))
    return bytes(content)


async def _validate_reply(response: aiohttp.ClientResponse) -> None:
    """Refuse a reply that is not a success, reading at most a short error body."""
    if response.status < HTTPStatus.MULTIPLE_CHOICES:
        return
    body = await response.content.read(MAX_ERROR_BYTES)
    raise read_failure(response.status, body)


@asynccontextmanager
async def _validate_paid_request(configuration: Configuration) -> AsyncGenerator[None]:
    """Name what a failed paid request may have cost; nothing retries it."""
    try:
        yield
    except aiohttp.ClientConnectorError:
        # The connection failed before the request was sent, so nothing was billed.
        raise OpenRouterError(ErrorCode.TRANSPORT, OPENROUTER_UNREACHABLE) from None
    except aiohttp.ClientError:
        raise OpenRouterError(ErrorCode.UNCERTAIN, REQUEST_UNCERTAIN) from None
    except TimeoutError:
        seconds = configuration.settings.request_timeout_seconds
        raise OpenRouterError(ErrorCode.TIMEOUT, REQUEST_TIMEOUT.format(seconds=seconds)) from None


def _parse_reply(content: bytes) -> Json:
    """Read a JSON reply whose size the download limit already bounds."""
    try:
        text = content.decode("utf-8")
        return parse_json(text, max_bytes=len(content) + 1)
    except (UnicodeError, OpenRouterError):
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


async def _download(
    url: str, configuration: Configuration, *, is_authorized: bool, is_missing_ok: bool = False
) -> bytes:
    """Read one address that bills nothing, retrying busy replies and dropped connections a few times.

    With is_missing_ok, a 404 reads as an empty body; the JSON replies that use it are never empty.
    """
    for attempt in range(GET_ATTEMPTS):
        delay = float(2**attempt)
        is_last = attempt == GET_ATTEMPTS - 1
        try:
            async with (
                _create_session(configuration, is_authorized=is_authorized) as session,
                session.get(url, allow_redirects=False) as response,
            ):
                if response.status in RETRY_STATUSES and not is_last:
                    delay = _read_retry_delay(response.headers.get("Retry-After"), delay)
                elif is_missing_ok and response.status == HTTPStatus.NOT_FOUND:
                    return b""
                else:
                    await _validate_reply(response)
                    return await _read_body(response, configuration)
        except (aiohttp.ClientError, TimeoutError):
            if is_last:
                raise OpenRouterError(ErrorCode.TRANSPORT, OPENROUTER_UNREACHABLE) from None
        await asyncio.sleep(delay)
    raise OpenRouterError(ErrorCode.TRANSPORT, OPENROUTER_UNREACHABLE)


def _read_retry_delay(header: str | None, delay: float) -> float:
    """Wait as long as OpenRouter asks, within bounds, or the given delay when it does not say."""
    try:
        seconds = float(header) if header else delay
    except ValueError:
        seconds = delay
    return min(max(seconds, MIN_RETRY_SECONDS), MAX_RETRY_SECONDS)


async def send_json(url: str, body: Mapping[str, Json], configuration: Configuration) -> Json:
    """Send one paid JSON request and return its parsed JSON reply."""
    async with (
        _validate_paid_request(configuration),
        _create_session(configuration) as session,
        session.post(url, json=body, allow_redirects=False) as response,
    ):
        await _validate_reply(response)
        content = await _read_body(response, configuration)
    return _parse_reply(content)


async def send_speech(url: str, body: Mapping[str, Json], configuration: Configuration) -> AudioReply:
    """Send one paid request whose reply is raw audio, and keep its media type."""
    async with (
        _validate_paid_request(configuration),
        _create_session(configuration) as session,
        session.post(url, json=body, allow_redirects=False) as response,
    ):
        await _validate_reply(response)
        content = await _read_body(response, configuration)
        media_type = response.headers.get("Content-Type", "")
    return AudioReply(content, media_type)


async def send_stream(url: str, body: Mapping[str, Json], configuration: Configuration) -> AsyncIterator[Json]:
    """Send one paid streamed request and yield each event it sends."""
    maximum = configuration.settings.max_download_megabytes * BYTES_PER_MEBIBYTE
    async with (
        _validate_paid_request(configuration),
        _create_session(configuration) as session,
        session.post(url, json=body, allow_redirects=False) as response,
    ):
        await _validate_reply(response)
        async for event in read_events(response, maximum):
            yield event


async def download_video(url: str, configuration: Configuration) -> bytes:
    """Read a video job's status or its finished video from OpenRouter, the only host the key is sent to."""
    if not url.startswith(VIDEO_CONTENT_PREFIX):
        raise OpenRouterError(ErrorCode.TRANSPORT, VIDEO_URL_UNEXPECTED)
    return await _download(url, configuration, is_authorized=True)


async def download_listing[T: Reply](url: str, reply: type[T], configuration: Configuration) -> T | None:
    """Read one of OpenRouter's public model listings without the key, or None when it lists no such model."""
    content = await _download(url, configuration, is_authorized=False, is_missing_ok=True)
    if not content:
        return None
    try:
        return reply.model_validate_json(content)
    except ValidationError:
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


async def download_media(url: str, configuration: Configuration) -> bytes:
    """Download media a reply links on a provider's host, without the key."""
    if not url.startswith("https://"):
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
    return await _download(url, configuration, is_authorized=False)


__all__ = ["download_listing", "download_media", "download_video", "send_json", "send_speech", "send_stream"]
