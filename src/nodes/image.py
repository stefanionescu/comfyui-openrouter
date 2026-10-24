"""Generate or edit images with any OpenRouter image model."""

from __future__ import annotations

import io as memory
from typing import TYPE_CHECKING, override
from dataclasses import dataclass

from comfy_api.latest import io
from comfy_execution.graph import ExecutionBlocker

from .base import PaidNode
from .inputs import build_request_inputs
from ..comfy.media import decode_image, encode_images
from ..config.media import SVG_MEDIA_TYPE
from ..state.images import ImageRequest
from ..comfy.execution import send_request, wait_for_task, wait_for_thread
from ..config.namespace import MENUS, NODE_PREFIX
from ..openrouter.images import ImageOperation
from ..config.generation.images import MAX_SIZE, COMPRESSION, FIELD_VALUES, COMPRESSED_FORMATS
from ..config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP
from ..config.generation.models import DEFAULT_MODELS

if TYPE_CHECKING:
    import torch

    from ..state import Json
    from ..state.images import ImageResult
    from ..state.options import Options


# The image fields, compression, exact size, n, and references; a field left at default sends nothing.
# The format, the last field, has a tooltip that explains its name.
FIELDS = (
    *(
        io.Combo.Input(field, options=[MODEL_DEFAULT, *values], default=MODEL_DEFAULT)
        for field, values in FIELD_VALUES.items()
        if field != 'output_format'
    ),
    io.Combo.Input(
        'output_format',
        options=[MODEL_DEFAULT, *FIELD_VALUES['output_format']],
        default=MODEL_DEFAULT,
        tooltip='The file format of the images. svg needs a model that draws vectors.',
    ),
    io.Int.Input(
        'output_compression',
        default=COMPRESSION['DEFAULT'],
        min=0,
        max=COMPRESSION['MAX'],
        advanced=True,
        tooltip='The quality of JPEG and WebP images; higher keeps more detail.',
    ),
    *(
        io.Int.Input(
            side,
            default=0,
            min=0,
            max=MAX_SIZE,
            advanced=True,
            tooltip=f'The exact image {side} in pixels, sent with {other}; 0 sends no size. '
            'An exact size needs resolution and aspect_ratio at default.',
        )
        for side, other in (('width', 'height'), ('height', 'width'))
    ),
    io.Int.Input('n', default=1, min=1, tooltip='How many images to make, within what the model lists.'),
    io.Image.Input(
        'references',
        optional=True,
        tooltip='Images to edit or combine: one, a batch, or a list. Create List joins several Load Image nodes.',
    ),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ImageGenerateInputs:
    """The saved inputs of Image: Generate, by input name, except the run number."""

    prompt: str
    model: str
    seed: int
    resolution: str = MODEL_DEFAULT
    aspect_ratio: str = MODEL_DEFAULT
    quality: str = MODEL_DEFAULT
    background: str = MODEL_DEFAULT
    output_format: str = MODEL_DEFAULT
    output_compression: int = COMPRESSION['DEFAULT']
    width: int = 0
    height: int = 0
    n: int = 1
    references: list[torch.Tensor] | None = None
    options: Options | None = None


class ImageGenerate(PaidNode):
    """Send one image request and return its raster images, their masks, and any SVG files."""

    record = ImageGenerateInputs

    list_inputs = frozenset({'references'})

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the prompt, the model, every image field, and the reference sockets."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Image: Generate',
            category=MENUS['IMAGE'],
            description='Generate or edit images with any OpenRouter image model.',
            inputs=[
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['images'], tooltip=MODEL_TOOLTIP),
                *FIELDS,
                *build_request_inputs(has_seed=True),
                io.String.Input('prompt', multiline=True, default='', tooltip='What to draw or change.'),
            ],
            outputs=[
                io.Image.Output('images', display_name='images', is_output_list=True),
                io.Mask.Output('masks', display_name='masks', is_output_list=True),
                io.SVG.Output('svg', display_name='svg'),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def send(cls, image: ImageGenerateInputs) -> io.NodeOutput:
        """Encode the references inside the owned task, send, and split raster images from SVG files."""
        values = {
            'resolution': image.resolution,
            'aspect_ratio': image.aspect_ratio,
            'quality': image.quality,
            'background': image.background,
            'output_format': image.output_format,
        }
        # A field left at the model's default sends nothing, and compression applies only to JPEG and WebP.
        fields: dict[str, Json] = {field: value for field, value in values.items() if value != MODEL_DEFAULT}
        if image.output_format in COMPRESSED_FORMATS:
            fields['output_compression'] = image.output_compression

        async def send_encoded() -> io.NodeOutput:
            """Encode the references inside the owned task, then send the request."""
            urls = await wait_for_thread(
                lambda: tuple(url for batch in image.references or () for url in encode_images(batch))
            )
            request = ImageRequest(
                model_id=image.model.strip(),
                prompt=image.prompt,
                reference_urls=urls,
                n=image.n,
                width=image.width,
                height=image.height,
                seed=image.seed,
                fields=fields,
                options=image.options,
            )
            operation = ImageOperation(request)
            return await send_request(operation.send, build_outputs, cls.hidden.unique_id, validate=operation.validate)

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

        return await wait_for_task(send_encoded())


__all__ = ['ImageGenerate']
