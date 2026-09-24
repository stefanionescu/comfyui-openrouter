"""Make a video with any OpenRouter video model, from text, frames, or references."""

from __future__ import annotations

import asyncio
import io as memory
from ..base import PaidNode
from typing import TYPE_CHECKING
from ...comfy.media import encode_images
from ...comfy.runtime import get_runtime
from ...types.videos import VideoRequest
from ...config.media import WAV_URL_PREFIX
from comfy_api.latest import io, InputImpl
from ...config.messages.videos import IMAGE_BATCH
from ...types.errors import ErrorCode, OpenRouterError
from ...config.namespace import VIDEO_MENU, NODE_PREFIX
from ..inputs import encode_media, build_request_inputs
from ...openrouter.videos.operation import VideoOperation
from ...config.generation.models import DEFAULT_VIDEO_MODEL
from ...comfy.execution import wait_for_thread, send_request, wait_for_task
from ...config.generation.inputs import MODEL_INPUT, MODEL_DEFAULT, MODEL_TOOLTIP
from ...config.generation.videos import (
    RESOLUTIONS,
    MAX_DURATION,
    UPSCALE_STEP,
    ASPECT_RATIOS,
    AUDIO_CHOICES,
    MAX_CREATIVITY,
    CREATIVITY_STEP,
    MAX_UPSCALE_FACTOR,
)

if TYPE_CHECKING:
    import torch
    from comfy_api.latest import Input
    from ...types.options import Options
    from collections.abc import Mapping, Sequence


# The first and last frame take one image each; each reference socket takes one item, a batch, or a list, and
# everything connected goes in one request.
MEDIA = (
    *(
        io.Image.Input(
            frame, display_name=frame.replace("_", " "), optional=True, tooltip=f"The image the video {end}."
        )
        for frame, end in (("first_frame", "starts from"), ("last_frame", "ends on"))
    ),
    io.Image.Input(
        "reference_images",
        display_name="reference images",
        optional=True,
        tooltip="Images the video follows: one, a batch, or a list. Leave the frames empty to use references.",
    ),
    io.Video.Input(
        "reference_videos",
        display_name="reference videos",
        optional=True,
        tooltip="Videos the video follows. Create List joins several.",
    ),
    io.Audio.Input(
        "reference_audio",
        display_name="reference audio",
        optional=True,
        tooltip="Audio the video follows. Create List joins several.",
    ),
)


# The duration, size, and sound, then the upscale settings of an upscaling model; 0 and model default send nothing.
CONTROLS = (
    io.Int.Input(
        "duration",
        default=0,
        min=0,
        max=MAX_DURATION,
        tooltip="The length in seconds; 0 leaves it to the model.",
    ),
    io.Combo.Input("resolution", options=list(RESOLUTIONS), default=MODEL_DEFAULT),
    io.Combo.Input("aspect_ratio", display_name="aspect ratio", options=list(ASPECT_RATIOS), default=MODEL_DEFAULT),
    io.Combo.Input("generate_audio", display_name="generate audio", options=list(AUDIO_CHOICES), default=MODEL_DEFAULT),
    io.Float.Input(
        "upscale_factor",
        display_name="upscale factor",
        default=0.0,
        min=0.0,
        max=MAX_UPSCALE_FACTOR,
        step=UPSCALE_STEP,
        advanced=True,
        tooltip="How much an upscaling model enlarges the video; 0 sends nothing.",
    ),
    io.Float.Input(
        "creativity",
        default=0.0,
        min=0.0,
        max=MAX_CREATIVITY,
        step=CREATIVITY_STEP,
        advanced=True,
        tooltip="How freely an upscaling model adds detail; 0 sends nothing.",
    ),
)


def _encode_frames(frames: Mapping[str, Sequence[torch.Tensor] | None]) -> dict[str, str]:
    """Encode each connected frame, refusing more than one image, since a frame is one image."""
    encoded: dict[str, str] = {}
    for frame, batches in frames.items():
        images = list(batches or ())
        if sum(batch.shape[0] for batch in images) > 1:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, IMAGE_BATCH)
        if images:
            encoded[frame] = encode_images(images[0])[0]
    return encoded


class VideoGenerate(PaidNode):
    """Submit one video job, record it, wait for it, and return the video."""

    list_inputs = frozenset({"first_frame", "last_frame", "reference_images", "reference_videos", "reference_audio"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the prompt, the model, every video control, the frames, and the reference sockets."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Video: Generate",
            category=VIDEO_MENU,
            description="Make a video with any OpenRouter video model, from text, frames, or references.",
            inputs=[
                io.String.Input(MODEL_INPUT, default=DEFAULT_VIDEO_MODEL, tooltip=MODEL_TOOLTIP),
                *CONTROLS,
                *MEDIA,
                *build_request_inputs(has_seed=True),
                io.String.Input(
                    "prompt",
                    multiline=True,
                    default="",
                    placeholder="prompt",
                    tooltip="What the video shows. It may be empty when a first frame is connected.",
                ),
            ],
            outputs=[io.Video.Output("video", display_name="video")],
            is_input_list=True,
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        prompt: str,
        model: str,
        seed: int,
        duration: int = 0,
        resolution: str = MODEL_DEFAULT,
        aspect_ratio: str = MODEL_DEFAULT,
        generate_audio: str = MODEL_DEFAULT,
        upscale_factor: float = 0.0,
        creativity: float = 0.0,
        first_frame: list[torch.Tensor] | None = None,
        last_frame: list[torch.Tensor] | None = None,
        reference_images: list[torch.Tensor] | None = None,
        reference_videos: list[Input.Video] | None = None,
        reference_audio: list[Input.Audio] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Encode the frames and references inside the owned task, then submit, record, and wait."""
        frames = {"first_frame": first_frame, "last_frame": last_frame}

        async def send_encoded() -> io.NodeOutput:
            """Encode the media inside the owned task, then send the request."""
            frame_urls, (image_urls, video_urls, clips) = await wait_for_thread(
                lambda: (_encode_frames(frames), encode_media(reference_images, reference_videos, reference_audio))
            )
            references = (
                *(("image", url) for url in image_urls),
                *(("video", url) for url in video_urls),
                *(("audio", WAV_URL_PREFIX + clip) for clip in clips),
            )
            # A control left at 0 or at the model's default sends nothing.
            request = VideoRequest(
                model_id=model.strip(),
                prompt=prompt,
                duration=duration or None,
                resolution=resolution if resolution != MODEL_DEFAULT else None,
                aspect_ratio=aspect_ratio if aspect_ratio != MODEL_DEFAULT else None,
                frame_urls=frame_urls,
                references=references,
                generate_audio={"on": True, "off": False}.get(generate_audio),
                seed=seed,
                upscale_factor=upscale_factor or None,
                creativity=creativity or None,
                options=options,
            )
            # ComfyUI reads the MP4 from memory, so no temporary file is written.
            return await send_request(
                VideoOperation(request, get_runtime().jobs),
                lambda content: io.NodeOutput(InputImpl.VideoFromFile(memory.BytesIO(content))),
            )

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["VideoGenerate"]
