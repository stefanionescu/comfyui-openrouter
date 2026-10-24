"""Send one rank request and read the documents in order of relevance."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

from .models import validate_model
from .options import build_request_body
from .operation import validate_upload_size
from .transport import send_json, read_reply
from .embeddings import validate_search_items
from ..state.errors import ErrorCode, OpenRouterError
from ..state.search import RankedItem, RankResult
from ..state.replies import RankReply
from ..config.openrouter import ENDPOINT_URLS
from ..config.messages.run import REPLY_UNREADABLE
from ..config.messages.inputs import QUERY_EMPTY

if TYPE_CHECKING:
    from ..state import Json
    from ..state.search import RankRequest
    from ..state.settings import Settings, Configuration


@dataclass(frozen=True, slots=True)
class RankOperation:
    """One rank request.

    Attributes:
        request: The request to validate and send.

    """

    request: RankRequest

    def validate(self, settings: Settings) -> None:
        """Refuse an empty query, no documents, and media over the upload limit."""
        request = self.request
        if not request.query.strip():
            raise OpenRouterError(ErrorCode.INVALID_INPUT, QUERY_EMPTY)
        validate_search_items(request.texts, request.image_urls)
        validate_upload_size(request.image_urls, settings)

    async def send(self, configuration: Configuration) -> RankResult:
        """Check the model and send the query and documents; the reply lists them highest relevance first."""
        request = self.request
        inputs = ['image'] if request.image_urls else []
        await validate_model(request.model_id, 'rerank', configuration.settings, inputs)
        documents: list[Json] = [*request.texts, *({'image': url} for url in request.image_urls)]
        body: dict[str, Json] = {'model': request.model_id, 'query': request.query, 'documents': documents}
        if request.top_n > 0:
            body['top_n'] = request.top_n
        document = await send_json(
            ENDPOINT_URLS['rerank'], build_request_body(body, request.options, 'rerank'), configuration
        )
        reply = read_reply(RankReply, document)
        if any(not 0 <= item.index < len(documents) for item in reply.results):
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
        return RankResult(tuple(RankedItem(item.index, item.relevance_score) for item in reply.results))


__all__ = ['RankOperation']
