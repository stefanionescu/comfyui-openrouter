"""Make a video with any OpenRouter video model, from text, frames, or references."""

from __future__ import annotations

import io as memory
from typing import TYPE_CHECKING, override
from dataclasses import dataclass

from comfy_api.latest import InputImpl, io

from ..base import PaidNode
from ..inputs import encode_media, build_request_inputs
from ...comfy.media import encode_images
from ...config.media import WAV
from ...state.errors import ErrorCode, OpenRouterError
from ...state.videos import VideoRequest
from ...comfy.runtime import get_runtime
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ...config.namespace import MENUS, NODE_PREFIX
from ...config.messages.videos import IMAGE_BATCH
from ...config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP
from ...config.generation.models import DEFAULT_MODELS
from ...config.generation.videos import STEPS, RESOLUTIONS, ASPECT_RATIOS, AUDIO_CHOICES
from ...openrouter.videos.operation import VideoOperation

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    import torch
    from comfy_api.latest import Input

    from ...state.options import Options


# The first and last frame take one image each; each reference socket takes one item, a batch, or a list, and
# everything connected goes in one request.
MEDIA = (
    *(
        io.Image.Input(frame, optional=True, tooltip=f'The image the video {end}.')
        for frame, end in (('first_frame', 'starts from'), ('last_frame', 'ends on'))
    ),
    io.Image.Input(
        'reference_images',
        optional=True,
        tooltip='Images the video follows: one, a batch, or a list. To use them, leave first_frame and last_frame '
        'empty.',
    ),
    io.Video.Input(
        'reference_videos',
        optional=True,
        tooltip='Videos the video follows. Create List joins several.',
    ),
    io.Audio.Input(
        'reference_audio',
        optional=True,
        tooltip='Audio the video follows. Create List joins several.',
    ),
)


# The duration, size, and sound, then the upscale settings of an upscaling model; 0 and default send nothing.
CONTROLS = (
    io.Int.Input(
        'duration',
        default=0,
        min=0,
        tooltip='The length in seconds; 0 leaves it to the model.',
    ),
    io.Combo.Input('resolution', options=list(RESOLUTIONS), default=MODEL_DEFAULT),
    io.Combo.Input('aspect_ratio', options=list(ASPECT_RATIOS), default=MODEL_DEFAULT),
    io.Combo.Input('generate_audio', options=list(AUDIO_CHOICES), default=MODEL_DEFAULT),
    io.Float.Input(
        'upscale_factor',
        default=0.0,
        min=0.0,
        step=STEPS['UPSCALE_FACTOR'],
        advanced=True,
        tooltip='How much an upscaling model enlarges the video; 0 sends nothing.',
    ),
    io.Float.Input(
        'creativity',
        default=0.0,
        min=0.0,
        step=STEPS['CREATIVITY'],
        advanced=True,
        tooltip='How freely an upscaling model adds detail; 0 sends nothing.',
    ),
)


def _encode_frames(frames: Mapping[str, Sequence[torch.Tensor] | None]) -> dict[str, str]:
    """Encode each connected frame, refusing more than one image, because a frame is one image."""
    encoded: dict[str, str] = {}
    for frame, batches in frames.items():
        images = list(batches or ())
        if sum(batch.shape[0] for batch in images) > 1:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, IMAGE_BATCH)
        if images:
            encoded[frame] = encode_images(images[0])[0]
    return encoded


@dataclass(frozen=True, slots=True, kw_only=True)
class VideoGenerateInputs:
    """The saved inputs of Video: Generate, by input name, except the run number."""

    prompt: str
    model: str
    seed: int
    duration: int = 0
    resolution: str = MODEL_DEFAULT
    aspect_ratio: str = MODEL_DEFAULT
    generate_audio: str = MODEL_DEFAULT
    upscale_factor: float = 0.0
    creativity: float = 0.0
    first_frame: list[torch.Tensor] | None = None
    last_frame: list[torch.Tensor] | None = None
    reference_images: list[torch.Tensor] | None = None
    reference_videos: list[Input.Video] | None = None
    reference_audio: list[Input.Audio] | None = None
    options: Options | None = None


class VideoGenerate(PaidNode):
    """Submit one video job, record it, wait for it, and return the video."""

    record = VideoGenerateInputs

    list_inputs = frozenset({'first_frame', 'last_frame', 'reference_images', 'reference_videos', 'reference_audio'})

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the prompt, the model, every video control, the frames, and the reference sockets."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Video: Generate',
            category=MENUS['VIDEO'],
            description='Make a video with any OpenRouter video model, from text, frames, or references.',
            inputs=[
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['videos'], tooltip=MODEL_TOOLTIP),
                *CONTROLS,
                *MEDIA,
                *build_request_inputs(has_seed=True),
                io.String.Input(
                    'prompt',
                    multiline=True,
                    default='',
                    tooltip='What the video shows. It can be empty when first_frame is connected.',
                ),
            ],
            outputs=[io.Video.Output('video', display_name='video')],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def send(cls, video: VideoGenerateInputs) -> io.NodeOutput:
        """Encode the frames and references inside the owned task, then submit, record, and wait."""
        frames = {'first_frame': video.first_frame, 'last_frame': video.last_frame}

        async def send_encoded() -> io.NodeOutput:
            """Encode the media inside the owned task, then send the request."""
            frame_urls, (image_urls, video_urls, clips) = await wait_for_thread(
                lambda: (
                    _encode_frames(frames),
                    encode_media(video.reference_images, video.reference_videos, video.reference_audio),
                )
            )
            references = (
                *(('image', url) for url in image_urls),
                *(('video', url) for url in video_urls),
                *(('audio', WAV['URL_PREFIX'] + clip) for clip in clips),
            )
            # A control left at 0 or at the model's default sends nothing.
            request = VideoRequest(
                model_id=video.model.strip(),
                prompt=video.prompt,
                duration=video.duration or None,
                resolution=video.resolution if video.resolution != MODEL_DEFAULT else None,
                aspect_ratio=video.aspect_ratio if video.aspect_ratio != MODEL_DEFAULT else None,
                frame_urls=frame_urls,
                references=references,
                generate_audio={'on': True, 'off': False}.get(video.generate_audio),
                seed=video.seed,
                upscale_factor=video.upscale_factor or None,
                creativity=video.creativity or None,
                options=video.options,
            )
            # ComfyUI reads the MP4 from memory, so the node writes no temporary file.
            operation = VideoOperation(request, get_runtime().jobs)
            return await send_request(
                operation.send,
                lambda content: io.NodeOutput(InputImpl.VideoFromFile(memory.BytesIO(content))),
                cls.hidden.unique_id,
                validate=operation.validate,
            )

        return await wait_for_task(send_encoded())


__all__ = ['VideoGenerate']
