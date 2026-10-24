"""Order text and images by how well they match a query."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, override
from dataclasses import dataclass

from comfy_api.latest import io
from comfy_execution.graph import ExecutionBlocker

from ..base import PaidNode, build_request_inputs
from .embed import IMAGES
from ...comfy.media import encode_images
from ...state.search import RankRequest
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ...config.namespace import MENUS, NODE_PREFIX
from ...openrouter.rerank import RankOperation
from ...config.generation.inputs import INPUT_NAMES, MODEL_TOOLTIP
from ...config.generation.models import DEFAULT_MODELS

if TYPE_CHECKING:
    import torch

    from ...state.search import RankResult
    from ...state.options import Options


@dataclass(frozen=True, slots=True, kw_only=True)
class SearchRankInputs:
    """The saved inputs of Search: Rank, by input name, except the run number."""

    query: str
    documents: list[str]
    model: str
    top_n: int
    images: list[torch.Tensor] | None = None
    options: Options | None = None


class SearchRank(PaidNode):
    """Send every document in one rank request, gathering the lists that reach the node."""

    record = SearchRankInputs

    list_inputs = frozenset({'images', 'documents'})

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Take input lists, so one request ranks the images of one Image: Generate run."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Search: Rank',
            category=MENUS['SEARCH'],
            description='Order text and images by how well they match a query.',
            inputs=[
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['rerank'], tooltip=MODEL_TOOLTIP),
                IMAGES,
                io.Int.Input(
                    'top_n',
                    default=0,
                    min=0,
                    tooltip='How many documents to keep; 0 keeps all.',
                ),
                *build_request_inputs(has_seed=False),
                io.String.Input('query', multiline=True, default='', tooltip='What the documents are ranked against.'),
                io.String.Input(
                    'documents', multiline=True, default='', tooltip='One document per line; blank lines are skipped.'
                ),
            ],
            outputs=[
                io.String.Output('texts', display_name='texts'),
                io.Image.Output('images', display_name='images', is_output_list=True),
                io.String.Output('scores', display_name='scores'),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def send(cls, ranking: SearchRankInputs) -> io.NodeOutput:
        """Encode every image inside the owned task, send all documents at once, and return them best first."""
        pictures = [batch[index : index + 1] for batch in ranking.images or () for index in range(batch.shape[0])]
        lines = tuple(line.strip() for text in ranking.documents for line in text.splitlines() if line.strip())

        def build_outputs(result: RankResult) -> io.NodeOutput:
            """Return the ranked texts, the ranked original images, and every score."""
            ranked_texts = [lines[item.index] for item in result.items if item.index < len(lines)]
            ranked_images = [pictures[item.index - len(lines)] for item in result.items if item.index >= len(lines)]
            scores = [
                {'index': item.index, 'kind': 'text' if item.index < len(lines) else 'image', 'score': item.score}
                for item in result.items
            ]
            return io.NodeOutput('\n'.join(ranked_texts), ranked_images or ExecutionBlocker(None), json.dumps(scores))

        async def send_encoded() -> io.NodeOutput:
            """Encode the images inside the owned task, then send the request."""
            urls = await wait_for_thread(lambda: tuple(url for image in pictures for url in encode_images(image)))
            request = RankRequest(
                model_id=ranking.model.strip(),
                query=ranking.query,
                texts=lines,
                image_urls=urls,
                top_n=ranking.top_n,
                options=ranking.options,
            )
            operation = RankOperation(request)
            return await send_request(operation.send, build_outputs, cls.hidden.unique_id, validate=operation.validate)

        return await wait_for_task(send_encoded())


__all__ = ['SearchRank']
