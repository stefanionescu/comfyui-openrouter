"""Turn text and images into embedding vectors and compare each item with the first."""

from __future__ import annotations

import json
import asyncio
from ..base import PaidNode
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ...comfy.media import encode_images
from ..inputs import build_request_inputs
from ...types.search import EmbeddingRequest
from ...config.generation.search import INPUT_TYPES
from ...openrouter.embeddings import EmbeddingOperation
from ...config.namespace import NODE_PREFIX, SEARCH_MENU
from ...config.generation.models import DEFAULT_EMBEDDING_MODEL
from ...comfy.execution import wait_for_thread, send_request, wait_for_task
from ...config.generation.inputs import MODEL_INPUT, MODEL_DEFAULT, MODEL_TOOLTIP

if TYPE_CHECKING:
    import torch
    from ...types.options import Options


# Every image of a batch or list is one item, compared or ranked with the texts in one request.
IMAGES = io.Image.Input(
    "images",
    optional=True,
    tooltip="Images to compare or rank, for models that read images: one, a batch, or a list.",
)


class SearchEmbed(PaidNode):
    """Send every item in one embedding request, gathering the lists that reach the node."""

    list_inputs = frozenset({"images", "texts"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Take input lists, so the images of one Image: Generate run go in one request."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Search: Embed",
            category=SEARCH_MENU,
            description="Turn text and images into embedding vectors and compare each item with the first.",
            inputs=[
                io.String.Input(MODEL_INPUT, default=DEFAULT_EMBEDDING_MODEL, tooltip=MODEL_TOOLTIP),
                IMAGES,
                io.Int.Input(
                    "dimensions",
                    default=0,
                    min=0,
                    advanced=True,
                    tooltip="Vector length for models that shorten vectors; 0 leaves it to the model.",
                ),
                io.Combo.Input(
                    "input_type",
                    display_name="input type",
                    options=list(INPUT_TYPES),
                    default=MODEL_DEFAULT,
                    advanced=True,
                    tooltip="A hint for models that embed queries and documents differently.",
                ),
                *build_request_inputs(has_seed=False),
                io.String.Input(
                    "texts", multiline=True, default="", tooltip="One item per line; blank lines are skipped."
                ),
            ],
            outputs=[
                io.String.Output("vectors", display_name="vectors"),
                io.String.Output("similarities", display_name="similarities"),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        texts: list[str],
        model: str,
        dimensions: int,
        input_type: str,
        images: list[torch.Tensor] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Encode every image inside the owned task, then send all items at once."""
        pictures = [batch[index : index + 1] for batch in images or () for index in range(batch.shape[0])]
        lines = tuple(line.strip() for text in texts for line in text.splitlines() if line.strip())

        async def send_encoded() -> io.NodeOutput:
            """Encode the images inside the owned task, then send the request."""
            urls = await wait_for_thread(lambda: tuple(url for image in pictures for url in encode_images(image)))
            request = EmbeddingRequest(
                model_id=model.strip(),
                texts=lines,
                image_urls=urls,
                dimensions=dimensions,
                input_type=input_type if input_type != MODEL_DEFAULT else None,
                options=options,
            )
            return await send_request(
                EmbeddingOperation(request),
                lambda result: io.NodeOutput(
                    json.dumps([list(vector) for vector in result.vectors]), json.dumps(list(result.similarities))
                ),
                cls.hidden.unique_id,
            )

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["IMAGES", "SearchEmbed"]
