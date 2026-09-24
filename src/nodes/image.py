"""Generate or edit images with any OpenRouter image model."""

from __future__ import annotations

import asyncio
import io as memory
from .base import PaidNode
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ..types.images import ImageRequest
from .inputs import build_request_inputs
from ..config.media import SVG_MEDIA_TYPE
from ..openrouter.images import ImageOperation
from comfy_execution.graph import ExecutionBlocker
from ..comfy.media import decode_image, encode_images
from ..config.namespace import IMAGE_MENU, NODE_PREFIX
from ..config.generation.models import DEFAULT_IMAGE_MODEL
from ..comfy.execution import wait_for_thread, send_request, wait_for_task
from ..config.generation.inputs import MODEL_INPUT, MODEL_DEFAULT, MODEL_TOOLTIP
from ..config.generation.images import (
    MAX_IMAGES,
    FIELD_LABELS,
    FIELD_VALUES,
    MAX_COMPRESSION,
    COMPRESSED_FORMATS,
    DEFAULT_COMPRESSION,
)

if TYPE_CHECKING:
    import torch
    from ..types import Json
    from ..types.options import Options
    from ..types.images import ImageResult


# Every image field, each starting at the model's default, which sends nothing, then the compression, the count,
# and the references. Every image of a batch or list goes in the one request, at its own size.
FIELDS = (
    *(
        io.Combo.Input(field, display_name=FIELD_LABELS[field], options=[MODEL_DEFAULT, *values], default=MODEL_DEFAULT)
        for field, values in FIELD_VALUES.items()
    ),
    io.Int.Input(
        "output_compression",
        display_name="compression",
        default=DEFAULT_COMPRESSION,
        min=0,
        max=MAX_COMPRESSION,
        advanced=True,
        tooltip="JPEG and WebP quality; higher keeps more detail.",
    ),
    io.Int.Input("count", default=1, min=1, max=MAX_IMAGES, tooltip="How many images to make."),
    io.Image.Input(
        "references",
        optional=True,
        tooltip="Images to edit or combine: one, a batch, or a list. Create List joins several Load Image nodes.",
    ),
)


class ImageGenerate(PaidNode):
    """Send one image request and return its raster images, their masks, and any SVG files."""

    list_inputs = frozenset({"references"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the prompt, the model, every image field, and the reference sockets."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Image: Generate",
            category=IMAGE_MENU,
            description="Generate or edit images with any OpenRouter image model.",
            inputs=[
                io.String.Input(MODEL_INPUT, default=DEFAULT_IMAGE_MODEL, tooltip=MODEL_TOOLTIP),
                *FIELDS,
                *build_request_inputs(has_seed=True),
                io.String.Input(
                    "prompt", multiline=True, default="", placeholder="prompt", tooltip="What to draw or change."
                ),
            ],
            outputs=[
                io.Image.Output("images", display_name="images", is_output_list=True),
                io.Mask.Output("masks", display_name="masks", is_output_list=True),
                io.SVG.Output("svg", display_name="svg"),
            ],
            is_input_list=True,
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        prompt: str,
        model: str,
        seed: int,
        resolution: str = MODEL_DEFAULT,
        aspect_ratio: str = MODEL_DEFAULT,
        quality: str = MODEL_DEFAULT,
        background: str = MODEL_DEFAULT,
        output_format: str = MODEL_DEFAULT,
        output_compression: int = DEFAULT_COMPRESSION,
        count: int = 1,
        references: list[torch.Tensor] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Encode the references inside the owned task, send, and split raster images from SVG files."""
        values = {
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "quality": quality,
            "background": background,
            "output_format": output_format,
        }
        # A field left at the model's default sends nothing, and compression applies only to JPEG and WebP.
        fields: dict[str, Json] = {field: value for field, value in values.items() if value != MODEL_DEFAULT}
        if output_format in COMPRESSED_FORMATS:
            fields["output_compression"] = output_compression

        async def send_encoded() -> io.NodeOutput:
            """Encode the references inside the owned task, then send the request."""
            urls = await wait_for_thread(
                lambda: tuple(url for batch in references or () for url in encode_images(batch))
            )
            request = ImageRequest(
                model_id=model.strip(),
                prompt=prompt,
                reference_urls=urls,
                count=count,
                seed=seed,
                fields=fields,
                options=options,
            )
            return await send_request(ImageOperation(request), build_outputs)

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

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["ImageGenerate"]
