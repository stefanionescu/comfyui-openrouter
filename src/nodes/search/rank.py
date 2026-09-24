"""Order text and images by how well they match a query."""

from __future__ import annotations

import json
import asyncio
from ..base import PaidNode
from ...tasks import owned_io
from comfy_api.latest import io
from ...state.search import RankRequest
from ...comfy.media import encode_images
from typing import ClassVar, TYPE_CHECKING
from ...state.capabilities import TextChoice
from ...execution.rerank import RankOperation
from comfy_execution.graph import ExecutionBlocker
from ..inputs import read_model, define_request_inputs
from .embed import read_list_model, define_search_model
from ...config.generation.search import MAX_SEARCH_ITEMS
from ...config.namespace import NODE_PREFIX, SEARCH_MENU
from ...config.generation.models import DEFAULT_RANK_MODEL
from ...comfy.execution import run_request, wait_for_execution

if TYPE_CHECKING:
    from ...state.search import RankResult
    from ...state.options import RequestOptions


class SearchRank(PaidNode):
    """Send every document in one rank request, gathering the lists that reach the node."""

    contract: ClassVar[str] = "search-rank-v1"

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Take input lists, so the images of one Image: Generate run are ranked in one request."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Search: Rank",
            category=SEARCH_MENU,
            description="Order text and images by how well they match a query.",
            inputs=[
                io.String.Input("query", multiline=True, default="", tooltip="What the documents are ranked against."),
                io.String.Input(
                    "documents", multiline=True, default="", tooltip="One document per line; blank lines are skipped."
                ),
                define_search_model("rerank", DEFAULT_RANK_MODEL),
                io.Int.Input(
                    "top_n",
                    display_name="keep best",
                    default=0,
                    min=0,
                    max=MAX_SEARCH_ITEMS,
                    tooltip="How many documents to keep; 0 keeps all.",
                ),
                *define_request_inputs(has_seed=False),
            ],
            outputs=[
                io.String.Output("texts", display_name="texts"),
                io.Image.Output("images", display_name="images", is_output_list=True),
                io.String.Output("scores", display_name="scores"),
            ],
            is_input_list=True,
        )

    @classmethod
    async def send(
        cls,
        *,
        query: list[str],
        documents: list[str],
        model: dict[str, object],
        top_n: list[int],
        options: list[RequestOptions] | None = None,
    ) -> io.NodeOutput:
        """Encode every image inside the owned task, send all documents at once, and return them best first."""
        values, images = read_list_model(model)
        selection = read_model("rerank", values, TextChoice)
        lines = tuple(line.strip() for text in documents for line in text.splitlines() if line.strip())

        def build_outputs(result: RankResult) -> io.NodeOutput:
            """Return the ranked texts, the ranked original images, and every score."""
            ranked_texts = [lines[item.index] for item in result.items if item.index < len(lines)]
            ranked_images = [images[item.index - len(lines)] for item in result.items if item.index >= len(lines)]
            scores = [
                {"index": item.index, "kind": "text" if item.index < len(lines) else "image", "score": item.score}
                for item in result.items
            ]
            return io.NodeOutput("\n".join(ranked_texts), ranked_images or ExecutionBlocker(None), json.dumps(scores))

        async def start() -> io.NodeOutput:
            """Encode the images inside the owned task, then send the request."""
            urls = await owned_io(lambda: tuple(url for image in images for url in encode_images(image)))
            request = RankRequest(
                model_id=selection.model_id,
                choice=selection.choice,
                query=query[0],
                texts=lines,
                image_urls=urls,
                top_n=top_n[0],
                options=options[0] if options else None,
            )
            return await run_request(RankOperation(request), build_outputs)

        return await wait_for_execution(asyncio.create_task(start()))


__all__ = ["SearchRank"]
