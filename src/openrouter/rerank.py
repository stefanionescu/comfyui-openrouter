"""Send one rank request and read the documents in order of relevance."""

from __future__ import annotations

from .transport import send_json
from typing import TYPE_CHECKING
from .models import validate_model
from pydantic import ValidationError
from ..types.replies import RankReply
from .options import build_request_body
from ..config.openrouter import RERANK_URL
from .operation import validate_upload_size
from .embeddings import validate_search_items
from ..config.messages.inputs import QUERY_EMPTY
from ..types.search import RankResult, RankedItem
from ..config.messages.run import REPLY_UNREADABLE
from ..types.errors import ErrorCode, OpenRouterError

if TYPE_CHECKING:
    from ..types import Json
    from ..types.search import RankRequest
    from ..types.settings import Settings, Configuration


class RankOperation:
    """One rank request."""

    def __init__(self, request: RankRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse an empty query, no documents, too many, and too much media."""
        request = self.request
        if not request.query.strip():
            raise OpenRouterError(ErrorCode.INVALID_INPUT, QUERY_EMPTY)
        validate_search_items(request.texts, request.image_urls)
        validate_upload_size(request.image_urls, settings)

    async def send(self, configuration: Configuration) -> RankResult:
        """Check the model and send the query and documents; the reply lists them highest relevance first."""
        request = self.request
        await validate_model(request.model_id, "rerank", configuration, ["image"] if request.image_urls else [])
        documents: list[Json] = [*request.texts, *({"image": url} for url in request.image_urls)]
        body: dict[str, Json] = {"model": request.model_id, "query": request.query, "documents": documents}
        if request.top_n > 0:
            body["top_n"] = request.top_n
        document = await send_json(RERANK_URL, build_request_body(body, request.options, "rerank"), configuration)
        try:
            reply = RankReply.model_validate(document)
        except ValidationError:
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        if any(not 0 <= item.index < len(documents) for item in reply.results):
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
        return RankResult(tuple(RankedItem(item.index, item.relevance_score) for item in reply.results))


__all__ = ["RankOperation"]
