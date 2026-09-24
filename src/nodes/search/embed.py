"""Turn text and images into embedding vectors and compare each item with the first."""

from __future__ import annotations

import json
import asyncio
from ..base import PaidNode
from ...tasks import owned_io
from comfy_api.latest import io
from ...comfy.media import encode_images
from ...state.capabilities import TextChoice
from ...state.search import EmbeddingRequest
from typing import cast, ClassVar, TYPE_CHECKING
from ...config.generation.inputs import MODEL_DEFAULT
from ...execution.embeddings import EmbeddingOperation
from ...config.namespace import NODE_PREFIX, SEARCH_MENU
from ...comfy.execution import run_request, wait_for_execution
from ...config.generation.models import DEFAULT_EMBEDDING_MODEL
from ..inputs import read_model, define_model_input, define_request_inputs
from ...config.generation.search import INPUT_TYPES, MAX_DIMENSIONS, MAX_SEARCH_IMAGES

if TYPE_CHECKING:
    import torch
    from collections.abc import Mapping
    from ...state.capabilities import Endpoint
    from ...state.options import RequestOptions


def define_search_model(endpoint: Endpoint, default_model: str) -> io.DynamicCombo.Input:
    """Build the model dropdown of a search node: image sockets appear for a model that reads images.

    Each socket can carry a list or a batch.
    """
    names = [f"image_{number}" for number in range(1, MAX_SEARCH_IMAGES + 1)]
    images = io.Autogrow.Input(
        "images",
        template=io.Autogrow.TemplateNames(io.Image.Input("image"), names=names, min=0),
        tooltip="Images to compare or rank; every image in a list or batch becomes one item.",
    )
    return define_model_input(
        endpoint,
        default_model,
        lambda choice: [images] if isinstance(choice, TextChoice) and "image" in choice.inputs else [],
        [images],
    )


def read_list_model(model: Mapping[str, object]) -> tuple[dict[str, object], tuple[torch.Tensor, ...]]:
    """Read a list node's dropdown, whose every value is a list, and split its images into single images."""
    values = {key: cast("list[object]", value)[0] for key, value in model.items() if key != "images"}
    slots = cast("Mapping[str, list[torch.Tensor] | None]", model.get("images") or {})
    ordered = sorted(slots.items(), key=lambda item: int(item[0].rsplit("_", 1)[1]))
    images = tuple(
        batch[index : index + 1]
        for _name, batches in ordered
        for batch in batches or ()
        for index in range(batch.shape[0])
    )
    return values, images


class SearchEmbed(PaidNode):
    """Send every item in one embedding request, gathering the lists that reach the node."""

    contract: ClassVar[str] = "search-embed-v1"

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
                define_search_model("embeddings", DEFAULT_EMBEDDING_MODEL),
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
    async def send(
        cls,
        *,
        texts: list[str],
        model: dict[str, object],
        dimensions: list[int],
        input_type: list[str],
        options: list[RequestOptions] | None = None,
    ) -> io.NodeOutput:
        """Encode every image inside the owned task, then send all items at once."""
        values, images = read_list_model(model)
        selection = read_model("embeddings", values, TextChoice)
        lines = tuple(line.strip() for text in texts for line in text.splitlines() if line.strip())

        async def start() -> io.NodeOutput:
            """Encode the images inside the owned task, then send the request."""
            urls = await owned_io(lambda: tuple(url for image in images for url in encode_images(image)))
            request = EmbeddingRequest(
                model_id=selection.model_id,
                choice=selection.choice,
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


__all__ = ["SearchEmbed", "define_search_model", "read_list_model"]
