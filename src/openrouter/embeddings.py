"""Send one embedding request and compare each item with the first."""

from __future__ import annotations

import math
from .transport import send_json
from typing import TYPE_CHECKING
from .models import validate_model
from pydantic import ValidationError
from .options import build_request_body
from ..types.replies import EmbeddingReply
from ..types.search import EmbeddingResult
from .operation import validate_upload_size
from ..config.openrouter import EMBEDDINGS_URL
from ..config.messages.run import REPLY_UNREADABLE
from ..types.errors import ErrorCode, OpenRouterError
from ..config.generation.search import MAX_SEARCH_ITEMS
from ..config.messages.inputs import SEARCH_ITEMS_EMPTY, SEARCH_ITEMS_LIMIT

if TYPE_CHECKING:
    from ..types import Json
    from collections.abc import Sequence
    from ..types.search import EmbeddingRequest
    from ..types.settings import Settings, Configuration


def validate_search_items(texts: Sequence[str], image_urls: Sequence[str]) -> None:
    """Refuse no items and too many."""
    count = len(texts) + len(image_urls)
    if count == 0:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, SEARCH_ITEMS_EMPTY)
    if count > MAX_SEARCH_ITEMS:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, SEARCH_ITEMS_LIMIT.format(maximum=MAX_SEARCH_ITEMS))


class EmbeddingOperation:
    """One embedding request."""

    def __init__(self, request: EmbeddingRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse no items, too many items, and too much media."""
        request = self.request
        validate_search_items(request.texts, request.image_urls)
        validate_upload_size(request.image_urls, settings)

    async def send(self, configuration: Configuration) -> EmbeddingResult:
        """Check the model, send the items, and compare each vector with the first by cosine similarity."""
        request = self.request
        await validate_model(request.model_id, "embeddings", configuration)
        # The endpoint takes one shape per request, so with images every item uses the content form.
        items: list[Json] = list(request.texts)
        if request.image_urls:
            texts: list[Json] = [{"content": [{"type": "text", "text": text}]} for text in request.texts]
            images: list[Json] = [
                {"content": [{"type": "image_url", "image_url": {"url": url}}]} for url in request.image_urls
            ]
            items = [*texts, *images]
        body: dict[str, Json] = {"model": request.model_id, "input": items, "encoding_format": "float"}
        if request.dimensions > 0:
            body["dimensions"] = request.dimensions
        if request.input_type is not None:
            body["input_type"] = request.input_type
        document = await send_json(
            EMBEDDINGS_URL, build_request_body(body, request.options, "embeddings"), configuration
        )
        try:
            reply = EmbeddingReply.model_validate(document)
        except ValidationError:
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        vectors = tuple(item.embedding for item in sorted(reply.vectors, key=lambda item: item.index))
        if len(vectors) != len(items):
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
        first = vectors[0]
        first_length = math.sqrt(math.fsum(value * value for value in first))
        similarities: list[float] = []
        for vector in vectors:
            length = first_length * math.sqrt(math.fsum(value * value for value in vector))
            dot = math.fsum(left * right for left, right in zip(first, vector, strict=False))
            similarities.append(dot / length if length else 0.0)
        return EmbeddingResult(vectors, tuple(similarities))


__all__ = ["EmbeddingOperation", "validate_search_items"]
