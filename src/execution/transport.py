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
from ..state.audio import AudioReply
from ..serialization import parse_json
from contextlib import asynccontextmanager
from ..errors import ErrorCode, ConnectorError
from ..config.messages.media import DOWNLOAD_LIMIT
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
    BYTES_PER_MEBIBYTE,
    VIDEO_CONTENT_PREFIX,
    ATTRIBUTION_CATEGORIES,
)

if TYPE_CHECKING:
    from ..state import Json
    from ..state.settings import ExecutionConfiguration
    from collections.abc import Mapping, AsyncIterator, AsyncGenerator


def _open_session(configuration: ExecutionConfiguration, *, is_authorized: bool = True) -> aiohttp.ClientSession:
    """Open one session for one request; the key goes only to OpenRouter, never to a provider's own host."""
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


async def _read_body(response: aiohttp.ClientResponse, configuration: ExecutionConfiguration) -> bytes:
    """Read a reply within the maximum download size."""
    maximum = configuration.settings.max_download_megabytes
    content = bytearray()
    async for chunk in response.content.iter_chunked(REPLY_CHUNK_BYTES):
        content.extend(chunk)
        if len(content) > maximum * BYTES_PER_MEBIBYTE:
            raise ConnectorError(ErrorCode.MEDIA, DOWNLOAD_LIMIT.format(maximum=maximum))
    return bytes(content)


async def _raise_failure(response: aiohttp.ClientResponse) -> None:
    """Refuse a reply that is not a success, reading at most a short error body."""
    if response.status < HTTPStatus.MULTIPLE_CHOICES:
        return
    body = await response.content.read(MAX_ERROR_BYTES)
    raise read_failure(response.status, body)


@asynccontextmanager
async def _paid_request(configuration: ExecutionConfiguration) -> AsyncGenerator[None]:
    """Name what a failed paid request may have cost; nothing retries it."""
    try:
        yield
    except aiohttp.ClientConnectorError:
        # The connection failed before the request was sent, so nothing was billed.
        raise ConnectorError(ErrorCode.TRANSPORT, OPENROUTER_UNREACHABLE) from None
    except aiohttp.ClientError:
        raise ConnectorError(ErrorCode.UNCERTAIN, REQUEST_UNCERTAIN) from None
    except TimeoutError:
        seconds = configuration.settings.request_timeout_seconds
        raise ConnectorError(ErrorCode.TIMEOUT, REQUEST_TIMEOUT.format(seconds=seconds)) from None


def _parse_reply(content: bytes) -> Json:
    """Read a JSON reply whose size the download limit already bounds."""
    try:
        text = content.decode("utf-8")
        return parse_json(text, max_bytes=len(content) + 1)
    except (UnicodeError, ConnectorError):
        raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


async def post_json(url: str, body: Mapping[str, Json], configuration: ExecutionConfiguration) -> Json:
    """Send one paid JSON request and return its parsed JSON reply."""
    async with (
        _paid_request(configuration),
        _open_session(configuration) as session,
        session.post(url, json=body, allow_redirects=False) as response,
    ):
        await _raise_failure(response)
        content = await _read_body(response, configuration)
    return _parse_reply(content)


async def post_audio(url: str, body: Mapping[str, Json], configuration: ExecutionConfiguration) -> AudioReply:
    """Send one paid request whose reply is raw audio, and keep its media type."""
    async with (
        _paid_request(configuration),
        _open_session(configuration) as session,
        session.post(url, json=body, allow_redirects=False) as response,
    ):
        await _raise_failure(response)
        content = await _read_body(response, configuration)
        media_type = response.headers.get("Content-Type", "")
    return AudioReply(content, media_type)


async def stream_events(
    url: str, body: Mapping[str, Json], configuration: ExecutionConfiguration
) -> AsyncIterator[Json]:
    """Send one paid streamed request and yield each event it sends."""
    maximum = configuration.settings.max_download_megabytes * BYTES_PER_MEBIBYTE
    async with (
        _paid_request(configuration),
        _open_session(configuration) as session,
        session.post(url, json=body, allow_redirects=False) as response,
    ):
        await _raise_failure(response)
        async for event in read_events(response, maximum):
            yield event


async def _get(url: str, configuration: ExecutionConfiguration, *, is_authorized: bool) -> bytes:
    """Read one address that bills nothing, retrying busy replies and dropped connections a few times."""
    for attempt in range(GET_ATTEMPTS):
        delay = float(2**attempt)
        is_last = attempt == GET_ATTEMPTS - 1
        try:
            async with (
                _open_session(configuration, is_authorized=is_authorized) as session,
                session.get(url, allow_redirects=False) as response,
            ):
                if response.status in RETRY_STATUSES and not is_last:
                    delay = _read_retry_delay(response.headers.get("Retry-After"), delay)
                else:
                    await _raise_failure(response)
                    return await _read_body(response, configuration)
        except (aiohttp.ClientError, TimeoutError):
            if is_last:
                raise ConnectorError(ErrorCode.TRANSPORT, OPENROUTER_UNREACHABLE) from None
        # A cancel ends the wait.
        await asyncio.sleep(delay)
    raise ConnectorError(ErrorCode.TRANSPORT, OPENROUTER_UNREACHABLE)


def _read_retry_delay(header: str | None, delay: float) -> float:
    """Wait as long as OpenRouter asks, within bounds, or the given delay when it does not say."""
    try:
        seconds = float(header) if header else delay
    except ValueError:
        seconds = delay
    return min(max(seconds, MIN_RETRY_SECONDS), MAX_RETRY_SECONDS)


async def get_video(url: str, configuration: ExecutionConfiguration) -> bytes:
    """Read a video job's status or its finished video from OpenRouter, the only host the key is sent to."""
    if not url.startswith(VIDEO_CONTENT_PREFIX):
        raise ConnectorError(ErrorCode.TRANSPORT, VIDEO_URL_UNEXPECTED)
    return await _get(url, configuration, is_authorized=True)


async def download_public(url: str, configuration: ExecutionConfiguration) -> bytes:
    """Download media a reply links on a provider's host, without the key."""
    if not url.startswith("https://"):
        raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
    return await _get(url, configuration, is_authorized=False)


__all__ = ["download_public", "get_video", "post_audio", "post_json", "stream_events"]
