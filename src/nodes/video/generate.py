"""Make a video with any OpenRouter video model, from text, frames, or references."""

from __future__ import annotations

import torch
import asyncio
import io as memory
from ..base import PaidNode
from typing import cast, TYPE_CHECKING
from ...comfy.runtime import get_runtime
from ...types.videos import VideoRequest
from ...config.messages.videos import IMAGE_BATCH
from comfy_api.latest import Input, InputImpl, io
from ...types.errors import ErrorCode, OpenRouterError
from ...config.namespace import VIDEO_MENU, NODE_PREFIX
from ..inputs import read_sockets, define_request_inputs
from ...openrouter.videos.operation import VideoOperation
from ...config.generation.models import DEFAULT_VIDEO_MODEL
from ...comfy.media import encode_audio, encode_video, encode_images
from ...comfy.execution import owned_io, run_request, wait_for_execution
from ...config.generation.inputs import MODEL_INPUT, MODEL_DEFAULT, MODEL_TOOLTIP
from ...config.generation.videos import (
    RESOLUTIONS,
    MAX_DURATION,
    ASPECT_RATIOS,
    AUDIO_CHOICES,
    MAX_UPSCALE_FACTOR,
    MAX_REFERENCE_AUDIO,
    MAX_REFERENCE_IMAGES,
    MAX_REFERENCE_VIDEOS,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from ...types.options import RequestOptions


def _define_media() -> list[io.Input]:
    """Offer the first and last frame, and one growing row of reference sockets for each kind."""
    media: list[io.Input] = [
        io.Image.Input(frame, display_name=frame.replace("_", " "), optional=True, tooltip="One image.")
        for frame in ("first_frame", "last_frame")
    ]
    for kind, template, count in (
        ("image", io.Image.Input("image"), MAX_REFERENCE_IMAGES),
        ("video", io.Video.Input("video"), MAX_REFERENCE_VIDEOS),
        ("audio", io.Audio.Input("audio"), MAX_REFERENCE_AUDIO),
    ):
        socket = "reference_audio" if kind == "audio" else f"reference_{kind}s"
        names = [f"reference_{kind}_{number}" for number in range(1, count + 1)]
        media.append(
            io.Autogrow.Input(
                socket,
                template=io.Autogrow.TemplateNames(template, names=names, min=0),
                tooltip=f"The {kind} references the video follows; leave the frames empty to use them.",
            )
        )
    return media


# The duration, size, and sound, then the upscale settings of an upscaling model; 0 and model default send nothing.
CONTROLS = (
    io.Int.Input(
        "duration",
        default=0,
        min=0,
        max=MAX_DURATION,
        tooltip="The length in seconds; 0 leaves it to the model. Video is priced per second.",
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
        step=0.1,
        advanced=True,
        tooltip="How much an upscaling model enlarges the video; 0 sends nothing.",
    ),
    io.Float.Input(
        "creativity",
        default=0.0,
        min=0.0,
        max=1.0,
        step=0.05,
        advanced=True,
        tooltip="How freely an upscaling model adds detail; 0 sends nothing.",
    ),
)


def _encode_frames(frames: Mapping[str, object]) -> dict[str, str]:
    """Encode each connected frame, refusing a batch, since a frame is one image."""
    encoded: dict[str, str] = {}
    for frame, image in frames.items():
        if not isinstance(image, torch.Tensor):
            continue
        if image.shape[0] != 1:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, IMAGE_BATCH)
        encoded[frame] = encode_images(image)[0]
    return encoded


def _encode_references(sockets: Mapping[str, Mapping[str, object] | None]) -> tuple[tuple[str, str], ...]:
    """Encode every connected reference image, video, and audio clip as a (kind, data URL) pair."""
    references: list[tuple[str, str]] = []
    for kind, slots in sockets.items():
        for value in read_sockets(slots):
            if isinstance(value, torch.Tensor):
                references += [(kind, url) for url in encode_images(value)]
            elif isinstance(value, Input.Video):
                references.append((kind, f"data:video/mp4;base64,{encode_video(value)}"))
            else:
                references.append((kind, f"data:audio/wav;base64,{encode_audio(cast('Input.Audio', value))}"))
    return tuple(references)


class VideoGenerate(PaidNode):
    """Submit one video job, record it, wait for it, and return the video."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the prompt, the model, every video control, the frames, and the reference sockets."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Video: Generate",
            category=VIDEO_MENU,
            description="Make a video with any OpenRouter video model, from text, frames, or references.",
            inputs=[
                io.String.Input(
                    "prompt",
                    multiline=True,
                    default="",
                    placeholder="prompt",
                    tooltip="What the video shows. It may be empty when a first frame is connected.",
                ),
                io.String.Input(MODEL_INPUT, default=DEFAULT_VIDEO_MODEL, tooltip=MODEL_TOOLTIP),
                *CONTROLS,
                *_define_media(),
                *define_request_inputs(has_seed=True),
            ],
            outputs=[io.Video.Output("video", display_name="video")],
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
        first_frame: torch.Tensor | None = None,
        last_frame: torch.Tensor | None = None,
        reference_images: dict[str, object] | None = None,
        reference_videos: dict[str, object] | None = None,
        reference_audio: dict[str, object] | None = None,
        options: RequestOptions | None = None,
    ) -> io.NodeOutput:
        """Encode the frames and references inside the owned task, then submit, record, and wait."""
        frames = {"first_frame": first_frame, "last_frame": last_frame}
        sockets = {"image": reference_images, "video": reference_videos, "audio": reference_audio}

        async def start() -> io.NodeOutput:
            """Encode the media inside the owned task, then send the request."""
            frame_urls, references = await owned_io(lambda: (_encode_frames(frames), _encode_references(sockets)))
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
            return await run_request(
                VideoOperation(request, get_runtime().jobs),
                lambda content: io.NodeOutput(InputImpl.VideoFromFile(memory.BytesIO(content))),
            )

        return await wait_for_execution(asyncio.create_task(start()))


__all__ = ["VideoGenerate"]
