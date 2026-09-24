"""Read OpenRouter's three public model lists, without a key."""

import aiohttp
import asyncio
from http import HTTPStatus
from datetime import UTC, datetime
from ..state.models import Snapshot
from .contracts import build_snapshot
from ..serialization import parse_json
from ..errors import ErrorCode, ConnectorError
from ..config.messages.models import MODELS_HTTP, MODEL_LIST_FORMAT, MODELS_UNREADABLE
from ..config.discovery import (
    MODELS_URL,
    IMAGE_MODELS_URL,
    MAX_SOURCE_BYTES,
    VIDEO_MODELS_URL,
    SOURCE_USER_AGENT,
    SOURCE_CHUNK_BYTES,
    SOURCE_TIMEOUT_SECONDS,
)


async def _read(session: aiohttp.ClientSession, url: str) -> str:
    """Read one public list within its byte limit and refuse redirects."""
    async with session.get(url, allow_redirects=False) as response:
        if response.status != HTTPStatus.OK:
            raise ConnectorError(ErrorCode.DISCOVERY, MODELS_HTTP.format(status=response.status))
        content = bytearray()
        async for chunk in response.content.iter_chunked(SOURCE_CHUNK_BYTES):
            content.extend(chunk)
            if len(content) > MAX_SOURCE_BYTES:
                raise ConnectorError(ErrorCode.DISCOVERY, MODELS_UNREADABLE)
        return content.decode("utf-8")


async def read_public_models() -> Snapshot:
    """Read and validate the three public lists without changing the saved list."""
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=SOURCE_TIMEOUT_SECONDS),
            trust_env=False,
            cookie_jar=aiohttp.DummyCookieJar(),
            headers={"User-Agent": SOURCE_USER_AGENT},
        ) as session:
            # Await all reads even when one fails, so no task outlives the session.
            results = await asyncio.gather(
                _read(session, MODELS_URL),
                _read(session, IMAGE_MODELS_URL),
                _read(session, VIDEO_MODELS_URL),
                return_exceptions=True,
            )
        documents: list[str] = []
        for result in results:
            if isinstance(result, BaseException):
                raise result
            documents.append(result)
        models, images, videos = (parse_json(text, max_bytes=MAX_SOURCE_BYTES) for text in documents)
    except (aiohttp.ClientError, TimeoutError, UnicodeError):
        raise ConnectorError(ErrorCode.DISCOVERY, MODELS_UNREADABLE) from None
    except ConnectorError as error:
        if error.code is ErrorCode.DISCOVERY:
            raise
        raise ConnectorError(ErrorCode.DISCOVERY, MODEL_LIST_FORMAT) from None
    return build_snapshot(models, images, videos, datetime.now(UTC).isoformat())


__all__ = ["read_public_models"]
