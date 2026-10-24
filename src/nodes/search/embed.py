"""Turn text and images into embedding vectors and compare each item with the first."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, override
from dataclasses import dataclass

from comfy_api.latest import io

from ..base import PaidNode
from ..inputs import build_request_inputs
from ...comfy.media import encode_images
from ...state.search import EmbeddingRequest
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ...config.namespace import MENUS, NODE_PREFIX
from ...openrouter.embeddings import EmbeddingOperation
from ...config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP
from ...config.generation.models import DEFAULT_MODELS
from ...config.generation.search import INPUT_TYPES

if TYPE_CHECKING:
    import torch

    from ...state.options import Options


# Every image of a batch or list is one item, compared or ranked with the texts in one request.
IMAGES = io.Image.Input(
    'images',
    optional=True,
    tooltip='Images to compare or rank, for models that read images: one, a batch, or a list.',
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SearchEmbedInputs:
    """The saved inputs of Search: Embed, by input name, except the run number."""

    texts: list[str]
    model: str
    dimensions: int
    input_type: str
    images: list[torch.Tensor] | None = None
    options: Options | None = None


class SearchEmbed(PaidNode):
    """Send every item in one embedding request, gathering the lists that reach the node."""

    record = SearchEmbedInputs

    list_inputs = frozenset({'images', 'texts'})

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Take input lists, so the images of one Image: Generate run go in one request."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Search: Embed',
            category=MENUS['SEARCH'],
            description='Turn text and images into embedding vectors and compare each item with the first.',
            inputs=[
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['embeddings'], tooltip=MODEL_TOOLTIP),
                IMAGES,
                io.Int.Input(
                    'dimensions',
                    default=0,
                    min=0,
                    advanced=True,
                    tooltip='Vector length for models that shorten vectors; 0 leaves it to the model.',
                ),
                io.Combo.Input(
                    'input_type',
                    options=list(INPUT_TYPES),
                    default=MODEL_DEFAULT,
                    advanced=True,
                    tooltip='A hint for models that embed queries and documents differently.',
                ),
                *build_request_inputs(has_seed=False),
                io.String.Input(
                    'texts', multiline=True, default='', tooltip='One item per line; blank lines are skipped.'
                ),
            ],
            outputs=[
                io.String.Output('vectors', display_name='vectors'),
                io.String.Output('similarities', display_name='similarities'),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def send(cls, embedding: SearchEmbedInputs) -> io.NodeOutput:
        """Encode every image inside the owned task, then send all items at once."""
        pictures = [batch[index : index + 1] for batch in embedding.images or () for index in range(batch.shape[0])]
        lines = tuple(line.strip() for text in embedding.texts for line in text.splitlines() if line.strip())

        async def send_encoded() -> io.NodeOutput:
            """Encode the images inside the owned task, then send the request."""
            urls = await wait_for_thread(lambda: tuple(url for image in pictures for url in encode_images(image)))
            request = EmbeddingRequest(
                model_id=embedding.model.strip(),
                texts=lines,
                image_urls=urls,
                dimensions=embedding.dimensions,
                input_type=embedding.input_type if embedding.input_type != MODEL_DEFAULT else None,
                options=embedding.options,
            )
            operation = EmbeddingOperation(request)
            return await send_request(
                operation.send,
                lambda result: io.NodeOutput(
                    json.dumps([list(vector) for vector in result.vectors]), json.dumps(list(result.similarities))
                ),
                cls.hidden.unique_id,
                validate=operation.validate,
            )

        return await wait_for_task(send_encoded())


__all__ = ['IMAGES', 'SearchEmbed']
