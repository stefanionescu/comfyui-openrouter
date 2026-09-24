"""Send one rank request and read the documents in order of relevance."""

from __future__ import annotations

from .transport import post_json
from typing import TYPE_CHECKING
from .options import apply_options
from pydantic import ValidationError
from ..state.replies import RankReply
from .operation import check_upload_size
from ..config.openrouter import RERANK_URL
from .embeddings import check_search_items
from ..errors import ErrorCode, ConnectorError
from ..config.messages.inputs import QUERY_EMPTY
from ..state.search import RankResult, RankedItem
from ..config.messages.run import REPLY_UNREADABLE

if TYPE_CHECKING:
    from ..state import Json
    from ..state.search import RankRequest
    from ..state.settings import Settings, ExecutionConfiguration


class RankOperation:
    """One rank request, refused before sending when its query or documents do not suit the model."""

    def __init__(self, request: RankRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse an empty query, no documents, too many, images the model cannot read, and too much media."""
        request, choice = self.request, self.request.choice
        if not request.query.strip():
            raise ConnectorError(ErrorCode.INVALID_INPUT, QUERY_EMPTY)
        check_search_items(request.texts, request.image_urls, choice.inputs if choice else None, request.model_id)
        check_upload_size(request.image_urls, settings)

    async def send(self, configuration: ExecutionConfiguration) -> RankResult:
        """Send the query and documents; the reply lists them highest relevance first."""
        request = self.request
        documents: list[Json] = [*request.texts, *({"image": url} for url in request.image_urls)]
        body: dict[str, Json] = {"model": request.model_id, "query": request.query, "documents": documents}
        if request.top_n > 0:
            body["top_n"] = request.top_n
        document = await post_json(RERANK_URL, apply_options(body, request.options, "rerank"), configuration)
        try:
            reply = RankReply.model_validate(document)
        except ValidationError:
            raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        if any(not 0 <= item.index < len(documents) for item in reply.results):
            raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
        return RankResult(tuple(RankedItem(item.index, item.relevance_score) for item in reply.results))


__all__ = ["RankOperation"]
