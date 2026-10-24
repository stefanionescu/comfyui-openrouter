"""Send every request that carries the OpenRouter key, the only outbound code that does.

The module sends every request once. A failed request stops the run, because a paid request may have reached
OpenRouter before its connection failed.
"""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from contextlib import asynccontextmanager

import aiohttp
from pydantic import ValidationError

from .streams import read_events
from .failures import read_failure
from ..state.audio import AudioReply
from ..config.units import BYTES_PER_MEBIBYTE
from ..state.errors import ErrorCode, OpenRouterError
from ..state.parsing import parse_json
from ..config.openrouter import REPLY_BYTES, ATTRIBUTION_HEADERS
from ..config.messages.run import REQUEST_TIMEOUT, REPLY_UNREADABLE, REQUEST_UNCERTAIN, OPENROUTER_UNREACHABLE
from ..config.messages.media import DOWNLOAD_LIMIT

if TYPE_CHECKING:
    from collections.abc import Mapping, AsyncIterator, AsyncGenerator

    from ..state import Json, Reply
    from ..state.settings import Settings, Configuration
    from ..state.credentials import Credential


def _create_session(settings: Settings, credential: Credential | None) -> aiohttp.ClientSession:
    """Open one session for one request; the key goes only to OpenRouter, never to a provider's own host.

    The session ignores proxy settings from the environment and cookies, and every request refuses redirects, so
    neither the key nor a reply can pass through another host. aiohttp sends a `GET` again when its connection
    drops, and its only switch for that is private, so this function turns it off.
    """
    headers = dict(ATTRIBUTION_HEADERS)
    if credential is not None:
        headers['Authorization'] = f'Bearer {credential.value}'
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=settings.request_timeout_seconds),
        trust_env=False,
        cookie_jar=aiohttp.DummyCookieJar(),
        headers=headers,
    )
    setattr(session, '_retry_connection', False)  # noqa: B010 # reason: aiohttp offers no public switch for its resend.
    return session


async def _read_body(response: aiohttp.ClientResponse, settings: Settings) -> bytes:
    """Read a reply within the maximum download size."""
    maximum = settings.max_download_megabytes
    content = bytearray()
    async for chunk in response.content.iter_chunked(REPLY_BYTES['CHUNK']):
        content.extend(chunk)
        if len(content) > maximum * BYTES_PER_MEBIBYTE:
            raise OpenRouterError(ErrorCode.MEDIA, DOWNLOAD_LIMIT.format(maximum=maximum))
    return bytes(content)


async def _validate_reply(response: aiohttp.ClientResponse) -> None:
    """Refuse a reply that is not a success, reading at most a short error body."""
    if response.status < HTTPStatus.MULTIPLE_CHOICES:
        return
    body = await response.content.read(REPLY_BYTES['MAX_ERROR'])
    raise read_failure(response.status, body)


@asynccontextmanager
async def _validate_paid_request(settings: Settings) -> AsyncGenerator[None]:
    """Name what a failed paid request may have cost; nothing retries it."""
    try:
        yield
    except aiohttp.ClientConnectorError:
        # The connection failed before the request went out, so OpenRouter billed nothing.
        raise OpenRouterError(ErrorCode.TRANSPORT, OPENROUTER_UNREACHABLE) from None
    except aiohttp.ClientError:
        raise OpenRouterError(ErrorCode.UNCERTAIN, REQUEST_UNCERTAIN) from None
    except TimeoutError:
        seconds = settings.request_timeout_seconds
        raise OpenRouterError(ErrorCode.TIMEOUT, REQUEST_TIMEOUT.format(seconds=seconds)) from None


def _parse_reply(content: bytes) -> Json:
    """Read a JSON reply whose size the download limit already bounds.

    The reply came with a success status, so the request ran and OpenRouter may bill it even when the reply is
    unreadable.
    """
    try:
        text = content.decode('utf-8')
        return parse_json(text, max_bytes=len(content) + 1)
    except (UnicodeError, OpenRouterError):
        raise OpenRouterError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE) from None


async def download(
    url: str, settings: Settings, *, credential: Credential | None = None, is_missing_ok: bool = False
) -> bytes:
    """Read one address that bills nothing, once.

    The key goes only with a credential, which callers pass only for OpenRouter's own addresses. With is_missing_ok,
    a 404 reads as an empty body; the JSON replies that use it are never empty.
    """
    try:
        async with (
            _create_session(settings, credential) as session,
            session.get(url, allow_redirects=False) as response,
        ):
            if is_missing_ok and response.status == HTTPStatus.NOT_FOUND:
                return b''
            await _validate_reply(response)
            return await _read_body(response, settings)
    except (aiohttp.ClientError, TimeoutError):
        raise OpenRouterError(ErrorCode.TRANSPORT, OPENROUTER_UNREACHABLE) from None


@asynccontextmanager
async def _post_paid(
    url: str, body: Mapping[str, Json], configuration: Configuration
) -> AsyncGenerator[aiohttp.ClientResponse]:
    """Send one paid JSON request, and hand over its reply once its status is a success."""
    async with (
        _validate_paid_request(configuration.settings),
        _create_session(configuration.settings, configuration.credential) as session,
        session.post(url, json=body, allow_redirects=False) as response,
    ):
        await _validate_reply(response)
        yield response


async def send_json(url: str, body: Mapping[str, Json], configuration: Configuration) -> Json:
    """Send one paid JSON request and return its parsed JSON reply."""
    async with _post_paid(url, body, configuration) as response:
        content = await _read_body(response, configuration.settings)
    return _parse_reply(content)


async def send_speech(url: str, body: Mapping[str, Json], configuration: Configuration) -> AudioReply:
    """Send one paid request whose reply is raw audio, and keep its media type."""
    async with _post_paid(url, body, configuration) as response:
        content = await _read_body(response, configuration.settings)
        media_type = response.headers.get('Content-Type', '')
    return AudioReply(content, media_type)


async def send_stream(url: str, body: Mapping[str, Json], configuration: Configuration) -> AsyncIterator[Json]:
    """Send one paid streamed request and yield each event it sends."""
    maximum = configuration.settings.max_download_megabytes * BYTES_PER_MEBIBYTE
    async with _post_paid(url, body, configuration) as response:
        async for event in read_events(response, maximum):
            yield event


def read_reply[T: Reply](reply: type[T], document: Json) -> T:
    """Read a parsed JSON reply as its record; a reply of another shape is unreadable."""
    try:
        return reply.model_validate(document)
    except ValidationError:
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


async def download_listing[T: Reply](url: str, reply: type[T], settings: Settings) -> T | None:
    """Read one of OpenRouter's public model listings without the key, or None when it lists no such model."""
    content = await download(url, settings, is_missing_ok=True)
    if not content:
        return None
    try:
        return reply.model_validate_json(content)
    except ValidationError:
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


async def download_media(url: str, settings: Settings) -> bytes:
    """Download media a reply links on a provider's host, without the key."""
    if not url.startswith('https://'):
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
    return await download(url, settings)


__all__ = ['download', 'download_listing', 'download_media', 'read_reply', 'send_json', 'send_speech', 'send_stream']
