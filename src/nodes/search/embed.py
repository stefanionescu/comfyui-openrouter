"""Turn text and images into embedding vectors and compare each item with the first."""

from __future__ import annotations

import json
import asyncio
from ..base import PaidNode
from comfy_api.latest import io
from typing import cast, TYPE_CHECKING
from ...comfy.media import encode_images
from ...types.search import EmbeddingRequest
from ...openrouter.embeddings import EmbeddingOperation
from ...config.namespace import NODE_PREFIX, SEARCH_MENU
from ..inputs import read_sockets, define_request_inputs
from ...config.generation.models import DEFAULT_EMBEDDING_MODEL
from ...comfy.execution import owned_io, run_request, wait_for_execution
from ...config.generation.inputs import MODEL_INPUT, MODEL_DEFAULT, MODEL_TOOLTIP
from ...config.generation.search import INPUT_TYPES, MAX_DIMENSIONS, MAX_SEARCH_IMAGES

if TYPE_CHECKING:
    import torch
    from ...types.options import RequestOptions


def define_images() -> io.Autogrow.Input:
    """Build a search node's growing row of image sockets; each socket can carry a list or a batch."""
    names = [f"image_{number}" for number in range(1, MAX_SEARCH_IMAGES + 1)]
    template = io.Autogrow.TemplateNames(io.Image.Input("image"), names=names, min=0)
    return io.Autogrow.Input(
        "images",
        template=template,
        tooltip="Images to compare or rank, for models that read images; each image in a list or batch is one item.",
    )


def read_images(images: dict[str, list[torch.Tensor]] | None) -> tuple[torch.Tensor, ...]:
    """Split the images of a list node's sockets, whose every value is a list of batches, into single images."""
    singles: list[torch.Tensor] = []
    for batches in read_sockets(images):
        for batch in cast("list[torch.Tensor]", batches):
            singles += [batch[index : index + 1] for index in range(batch.shape[0])]
    return tuple(singles)


class SearchEmbed(PaidNode):
    """Send every item in one embedding request, gathering the lists that reach the node."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Take input lists, so the images of one Image: Generate run go in one request."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Search: Embed",
            category=SEARCH_MENU,
            description="Turn text and images into embedding vectors and compare each item with the first.",
            inputs=[
                io.String.Input(
                    "texts", multiline=True, default="", tooltip="One item per line; blank lines are skipped."
                ),
                io.String.Input(MODEL_INPUT, default=DEFAULT_EMBEDDING_MODEL, tooltip=MODEL_TOOLTIP),
                define_images(),
                io.Int.Input(
                    "dimensions",
                    default=0,
                    min=0,
                    max=MAX_DIMENSIONS,
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
                *define_request_inputs(has_seed=False),
            ],
            outputs=[
                io.String.Output("vectors", display_name="vectors"),
                io.String.Output("similarities", display_name="similarities"),
            ],
            is_input_list=True,
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        texts: list[str],
        model: list[str],
        dimensions: list[int],
        input_type: list[str],
        images: dict[str, list[torch.Tensor]] | None = None,
        options: list[RequestOptions] | None = None,
    ) -> io.NodeOutput:
        """Encode every image inside the owned task, then send all items at once."""
        pictures = read_images(images)
        lines = tuple(line.strip() for text in texts for line in text.splitlines() if line.strip())

        async def start() -> io.NodeOutput:
            """Encode the images inside the owned task, then send the request."""
            urls = await owned_io(lambda: tuple(url for image in pictures for url in encode_images(image)))
            request = EmbeddingRequest(
                model_id=model[0].strip(),
                texts=lines,
                image_urls=urls,
                dimensions=dimensions[0],
                input_type=input_type[0] if input_type[0] != MODEL_DEFAULT else None,
                options=options[0] if options else None,
            )
            return await run_request(
                EmbeddingOperation(request),
                lambda result: io.NodeOutput(
                    json.dumps([list(vector) for vector in result.vectors]), json.dumps(list(result.similarities))
                ),
            )

        return await wait_for_execution(asyncio.create_task(start()))


__all__ = ["SearchEmbed", "define_images", "read_images"]
