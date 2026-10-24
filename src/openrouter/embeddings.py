"""Send one embedding request and compare each item with the first."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING
from dataclasses import dataclass

from .models import validate_model
from .options import build_request_body
from .operation import validate_upload_size
from .transport import send_json, read_reply
from ..state.errors import ErrorCode, OpenRouterError
from ..state.search import EmbeddingResult
from ..state.replies import EmbeddingReply
from ..config.openrouter import ENDPOINT_URLS
from ..config.messages.run import REPLY_UNREADABLE
from ..config.messages.inputs import SEARCH_ITEMS_EMPTY

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..state import Json
    from ..state.search import EmbeddingRequest
    from ..state.settings import Settings, Configuration


def validate_search_items(texts: Sequence[str], image_urls: Sequence[str]) -> None:
    """Refuse a request with no items."""
    count = len(texts) + len(image_urls)
    if count == 0:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, SEARCH_ITEMS_EMPTY)


@dataclass(frozen=True, slots=True)
class EmbeddingOperation:
    """One embedding request.

    Attributes:
        request: The request to validate and send.

    """

    request: EmbeddingRequest

    def validate(self, settings: Settings) -> None:
        """Refuse no items and media over the upload limit."""
        request = self.request
        validate_search_items(request.texts, request.image_urls)
        validate_upload_size(request.image_urls, settings)

    async def send(self, configuration: Configuration) -> EmbeddingResult:
        """Check the model, send the items, and compare each vector with the first by cosine similarity."""
        request = self.request
        inputs = ['image'] if request.image_urls else []
        await validate_model(request.model_id, 'embeddings', configuration.settings, inputs)
        # The endpoint takes one shape per request, so with images every item uses the content form.
        items: list[Json] = list(request.texts)
        if request.image_urls:
            texts: list[Json] = [{'content': [{'type': 'text', 'text': text}]} for text in request.texts]
            images: list[Json] = [
                {'content': [{'type': 'image_url', 'image_url': {'url': url}}]} for url in request.image_urls
            ]
            items = [*texts, *images]
        body: dict[str, Json] = {'model': request.model_id, 'input': items, 'encoding_format': 'float'}
        if request.dimensions > 0:
            body['dimensions'] = request.dimensions
        if request.input_type is not None:
            body['input_type'] = request.input_type
        document = await send_json(
            ENDPOINT_URLS['embeddings'], build_request_body(body, request.options, 'embeddings'), configuration
        )
        reply = read_reply(EmbeddingReply, document)
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


__all__ = ['EmbeddingOperation', 'validate_search_items']
