"""Send one embedding request and compare each item with the first."""

from __future__ import annotations

import math
from .transport import post_json
from typing import TYPE_CHECKING
from .options import apply_options
from pydantic import ValidationError
from .operation import check_upload_size
from ..state.replies import EmbeddingReply
from ..state.search import EmbeddingResult
from ..config.openrouter import EMBEDDINGS_URL
from ..errors import ErrorCode, ConnectorError
from ..config.messages.run import REPLY_UNREADABLE
from ..config.generation.search import MAX_SEARCH_ITEMS
from ..config.messages.inputs import INPUT_NOT_ACCEPTED, SEARCH_ITEMS_EMPTY, SEARCH_ITEMS_LIMIT

if TYPE_CHECKING:
    from ..state import Json
    from collections.abc import Sequence
    from ..state.search import EmbeddingRequest
    from ..state.settings import Settings, ExecutionConfiguration


def check_search_items(
    texts: Sequence[str], image_urls: Sequence[str], inputs: frozenset[str] | None, name: str
) -> None:
    """Refuse no items, too many, and images for a model that does not read them; None inputs means unknown."""
    count = len(texts) + len(image_urls)
    if count == 0:
        raise ConnectorError(ErrorCode.INVALID_INPUT, SEARCH_ITEMS_EMPTY)
    if count > MAX_SEARCH_ITEMS:
        raise ConnectorError(ErrorCode.INVALID_INPUT, SEARCH_ITEMS_LIMIT.format(maximum=MAX_SEARCH_ITEMS))
    if image_urls and inputs is not None and "image" not in inputs:
        raise ConnectorError(ErrorCode.INVALID_INPUT, INPUT_NOT_ACCEPTED.format(model=name, kind="image"))


class EmbeddingOperation:
    """One embedding request, refused before sending when its items do not suit the model."""

    def __init__(self, request: EmbeddingRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse no items, too many items, images the model cannot read, and too much media."""
        request, choice = self.request, self.request.choice
        check_search_items(request.texts, request.image_urls, choice.inputs if choice else None, request.model_id)
        check_upload_size(request.image_urls, settings)

    async def send(self, configuration: ExecutionConfiguration) -> EmbeddingResult:
        """Send the items and compare each vector with the first by cosine similarity."""
        request = self.request
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
        document = await post_json(EMBEDDINGS_URL, apply_options(body, request.options, "embeddings"), configuration)
        try:
            reply = EmbeddingReply.model_validate(document)
        except ValidationError:
            raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        vectors = tuple(item.embedding for item in sorted(reply.vectors, key=lambda item: item.index))
        if len(vectors) != len(items):
            raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
        first = vectors[0]
        first_length = math.sqrt(math.fsum(value * value for value in first))
        similarities: list[float] = []
        for vector in vectors:
            length = first_length * math.sqrt(math.fsum(value * value for value in vector))
            dot = math.fsum(left * right for left, right in zip(first, vector, strict=False))
            similarities.append(dot / length if length else 0.0)
        return EmbeddingResult(vectors, tuple(similarities))


__all__ = ["EmbeddingOperation", "check_search_items"]
