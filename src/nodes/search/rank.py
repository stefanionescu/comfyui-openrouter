"""Order text and images by how well they match a query."""

from __future__ import annotations

import json
import asyncio
from .embed import IMAGES
from ..base import PaidNode
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ...types.search import RankRequest
from ...comfy.media import encode_images
from ..inputs import build_request_inputs
from ...openrouter.rerank import RankOperation
from comfy_execution.graph import ExecutionBlocker
from ...config.namespace import NODE_PREFIX, SEARCH_MENU
from ...config.generation.models import DEFAULT_RANK_MODEL
from ...config.generation.inputs import MODEL_INPUT, MODEL_TOOLTIP
from ...comfy.execution import wait_for_thread, send_request, wait_for_task

if TYPE_CHECKING:
    import torch
    from ...types.options import Options
    from ...types.search import RankResult


class SearchRank(PaidNode):
    """Send every document in one rank request, gathering the lists that reach the node."""

    list_inputs = frozenset({"images", "documents"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Take input lists, so the images of one Image: Generate run are ranked in one request."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Search: Rank",
            category=SEARCH_MENU,
            description="Order text and images by how well they match a query.",
            inputs=[
                io.String.Input(MODEL_INPUT, default=DEFAULT_RANK_MODEL, tooltip=MODEL_TOOLTIP),
                IMAGES,
                io.Int.Input(
                    "top_n",
                    display_name="top n",
                    default=0,
                    min=0,
                    tooltip="How many documents to keep; 0 keeps all.",
                ),
                *build_request_inputs(has_seed=False),
                io.String.Input("query", multiline=True, default="", tooltip="What the documents are ranked against."),
                io.String.Input(
                    "documents", multiline=True, default="", tooltip="One document per line; blank lines are skipped."
                ),
            ],
            outputs=[
                io.String.Output("texts", display_name="texts"),
                io.Image.Output("images", display_name="images", is_output_list=True),
                io.String.Output("scores", display_name="scores"),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        query: str,
        documents: list[str],
        model: str,
        top_n: int,
        images: list[torch.Tensor] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Encode every image inside the owned task, send all documents at once, and return them best first."""
        pictures = [batch[index : index + 1] for batch in images or () for index in range(batch.shape[0])]
        lines = tuple(line.strip() for text in documents for line in text.splitlines() if line.strip())

        def build_outputs(result: RankResult) -> io.NodeOutput:
            """Return the ranked texts, the ranked original images, and every score."""
            ranked_texts = [lines[item.index] for item in result.items if item.index < len(lines)]
            ranked_images = [pictures[item.index - len(lines)] for item in result.items if item.index >= len(lines)]
            scores = [
                {"index": item.index, "kind": "text" if item.index < len(lines) else "image", "score": item.score}
                for item in result.items
            ]
            return io.NodeOutput("\n".join(ranked_texts), ranked_images or ExecutionBlocker(None), json.dumps(scores))

        async def send_encoded() -> io.NodeOutput:
            """Encode the images inside the owned task, then send the request."""
            urls = await wait_for_thread(lambda: tuple(url for image in pictures for url in encode_images(image)))
            request = RankRequest(
                model_id=model.strip(),
                query=query,
                texts=lines,
                image_urls=urls,
                top_n=top_n,
                options=options,
            )
            return await send_request(RankOperation(request), build_outputs, cls.hidden.unique_id)

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["SearchRank"]
