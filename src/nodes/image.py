"""Generate or edit images with any OpenRouter image model."""

from __future__ import annotations

import torch
import asyncio
import io as memory
from .base import PaidNode
from ..tasks import owned_io
from comfy_api.latest import io
from types import MappingProxyType
from ..state.images import ImageRequest
from ..config.media import SVG_MEDIA_TYPE
from ..state.models import ImageParameter
from ..state.capabilities import ImageChoice
from ..execution.images import ImageOperation
from typing import cast, ClassVar, TYPE_CHECKING
from comfy_execution.graph import ExecutionBlocker
from ..config.generation.inputs import MODEL_DEFAULT
from ..comfy.media import decode_image, encode_images
from ..config.namespace import IMAGE_MENU, NODE_PREFIX
from ..config.generation.models import DEFAULT_IMAGE_MODEL
from ..comfy.execution import run_request, wait_for_execution
from .inputs import read_model, define_model_input, define_request_inputs
from ..config.generation.images import (
    MAX_IMAGES,
    ALL_FORMATS,
    ENUM_FIELDS,
    FIELD_LABELS,
    ALL_QUALITIES,
    ALL_BACKGROUNDS,
    ALL_RESOLUTIONS,
    ALL_ASPECT_RATIOS,
    DEFAULT_COMPRESSION,
    MAX_REFERENCE_SOCKETS,
)

if TYPE_CHECKING:
    from ..state import Json
    from collections.abc import Mapping
    from ..state.images import ImageResult
    from ..state.options import RequestOptions


# What a written model ID may use, since the saved list does not describe it.
WRITTEN_PARAMETERS = MappingProxyType(
    {
        "resolution": ImageParameter(kind="enum", values=ALL_RESOLUTIONS),
        "aspect_ratio": ImageParameter(kind="enum", values=ALL_ASPECT_RATIOS),
        "quality": ImageParameter(kind="enum", values=ALL_QUALITIES),
        "background": ImageParameter(kind="enum", values=ALL_BACKGROUNDS),
        "output_format": ImageParameter(kind="enum", values=ALL_FORMATS),
        "output_compression": ImageParameter(kind="range", minimum=0, maximum=100),
        "n": ImageParameter(kind="range", minimum=1, maximum=MAX_IMAGES),
    }
)


def _define_children(choice: ImageChoice | None) -> list[io.Input]:
    """Show only the fields, count, and reference sockets this model accepts, or every one for a written ID.

    Each field starts at the model's default, which sends nothing. A reference socket can carry a batch,
    and every image in it is sent.
    """
    parameters = choice.parameters if choice else WRITTEN_PARAMETERS
    children: list[io.Input] = [
        io.Combo.Input(
            field,
            display_name=FIELD_LABELS[field],
            options=[MODEL_DEFAULT, *parameters[field].values],
            default=MODEL_DEFAULT,
        )
        for field in ENUM_FIELDS
        if field in parameters and parameters[field].kind == "enum"
    ]
    compression = parameters.get("output_compression")
    if compression is not None and compression.kind == "range":
        low, high = compression.minimum or 0, compression.maximum or 100
        children.append(
            io.Int.Input(
                "output_compression",
                display_name="compression",
                default=min(max(DEFAULT_COMPRESSION, low), high),
                min=low,
                max=high,
                advanced=True,
                tooltip="JPEG and WebP quality; higher keeps more detail.",
            )
        )
    count = parameters.get("n")
    if count is not None and count.kind == "range":
        low = count.minimum or 1
        children.append(
            io.Int.Input("count", display_name="images to make", default=low, min=low, max=count.maximum or low)
        )
    references = min(choice.max_references if choice else MAX_REFERENCE_SOCKETS, MAX_REFERENCE_SOCKETS)
    if references > 0:
        names = [f"reference_{number}" for number in range(1, references + 1)]
        children.append(
            io.Autogrow.Input(
                "references",
                template=io.Autogrow.TemplateNames(io.Image.Input("reference"), names=names, min=0),
                tooltip="Images to edit or combine, one per socket.",
            )
        )
    return children


def _read_fields(model: Mapping[str, object]) -> dict[str, Json]:
    """Read the chosen image fields under their wire names, leaving out every field left at the model's default."""
    fields: dict[str, Json] = {
        field: str(model[field]) for field in ENUM_FIELDS if model.get(field, MODEL_DEFAULT) != MODEL_DEFAULT
    }
    if "output_compression" in model:
        fields["output_compression"] = cast("int", model["output_compression"])
    return fields


class ImageGenerate(PaidNode):
    """Send one image request and return its raster images, their masks, and any SVG files."""

    contract: ClassVar[str] = "image-generate-v1"

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Build the model dropdown, one option per image model, with every field a written ID may use."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Image: Generate",
            category=IMAGE_MENU,
            description="Generate or edit images with any OpenRouter image model.",
            inputs=[
                io.String.Input(
                    "prompt", multiline=True, default="", placeholder="prompt", tooltip="What to draw or change."
                ),
                define_model_input("images", DEFAULT_IMAGE_MODEL, _define_children, _define_children(None)),
                *define_request_inputs(has_seed=True),
            ],
            outputs=[
                io.Image.Output("images", display_name="images", is_output_list=True),
                io.Mask.Output("masks", display_name="masks", is_output_list=True),
                io.SVG.Output("svg", display_name="svg"),
            ],
        )

    @classmethod
    async def send(
        cls, *, prompt: str, model: dict[str, object], seed: int, options: RequestOptions | None = None
    ) -> io.NodeOutput:
        """Encode the references inside the owned task, send, and split raster images from SVG files."""
        selection = read_model("images", model, ImageChoice)

        async def start() -> io.NodeOutput:
            """Encode the references inside the owned task, then send the request."""
            slots = cast("Mapping[str, object]", model.get("references") or {})
            ordered = sorted(slots.items(), key=lambda item: int(item[0].rsplit("_", 1)[1]))
            images = [image for _name, image in ordered if isinstance(image, torch.Tensor)]
            references = await owned_io(lambda: tuple(url for image in images for url in encode_images(image)))
            request = ImageRequest(
                model_id=selection.model_id,
                choice=selection.choice,
                prompt=prompt,
                reference_urls=references,
                count=cast("int", model.get("count", 1)),
                seed=seed,
                fields=_read_fields(model),
                options=options,
            )
            return await run_request(ImageOperation(request), build_outputs)

        def build_outputs(result: ImageResult) -> io.NodeOutput:
            """Decode the raster images with their masks; hand SVG files to ComfyUI's own SVG type."""
            raster = [output.content for output in result.outputs if output.media_type != SVG_MEDIA_TYPE]
            vectors = [output.content for output in result.outputs if output.media_type == SVG_MEDIA_TYPE]
            decoded = [decode_image(content) for content in raster]
            svg = io.SVG.Type([memory.BytesIO(content) for content in vectors]) if vectors else ExecutionBlocker(None)
            return io.NodeOutput(
                [pixels for pixels, _mask in decoded] or ExecutionBlocker(None),
                [mask for _pixels, mask in decoded] or ExecutionBlocker(None),
                svg,
            )

        return await wait_for_execution(asyncio.create_task(start()))


__all__ = ["ImageGenerate"]
