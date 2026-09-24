"""Make a video with any OpenRouter video model, from text, frames, or references."""

from __future__ import annotations

import torch
import asyncio
import io as memory
from ..base import PaidNode
from ...tasks import owned_io
from ...runtime import get_runtime
from ...state.videos import VideoRequest
from ...state.capabilities import VideoChoice
from ...errors import ErrorCode, ConnectorError
from typing import cast, ClassVar, TYPE_CHECKING
from ...config.messages.videos import IMAGE_BATCH
from comfy_api.latest import Input, InputImpl, io
from ...config.generation.inputs import MODEL_DEFAULT
from ...config.namespace import VIDEO_MENU, NODE_PREFIX
from ...execution.videos.operation import VideoOperation
from ...config.generation.models import DEFAULT_VIDEO_MODEL
from ...comfy.execution import run_request, wait_for_execution
from ...comfy.media import encode_audio, encode_video, encode_images
from ..inputs import read_model, define_model_input, define_request_inputs
from ...config.generation.videos import (
    AUDIO_CHOICES,
    DURATION_RANGE,
    ALL_RESOLUTIONS,
    DEFAULT_DURATION,
    ALL_ASPECT_RATIOS,
    MAX_REFERENCE_AUDIO,
    MAX_REFERENCE_IMAGES,
    MAX_REFERENCE_VIDEOS,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from ...state.options import RequestOptions


def _define_media(frame_types: tuple[str, ...], reference_types: frozenset[str]) -> list[io.Input]:
    """Offer the frames and the reference sockets the model accepts."""
    media: list[io.Input] = [
        io.Image.Input(frame, display_name=frame.replace("_", " "), optional=True, tooltip="One image.")
        for frame in ("first_frame", "last_frame")
        if frame in frame_types
    ]
    for kind, template, count in (
        ("image", io.Image.Input("image"), MAX_REFERENCE_IMAGES),
        ("video", io.Video.Input("video"), MAX_REFERENCE_VIDEOS),
        ("audio", io.Audio.Input("audio"), MAX_REFERENCE_AUDIO),
    ):
        if kind in reference_types:
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


def _define_upscale(
    upscale_range: tuple[float, float] | None, creativity: tuple[float, float] | None
) -> list[io.Input]:
    """Offer the upscale factor and creativity of an upscaling model."""
    controls: list[io.Input] = []
    if upscale_range is not None:
        low, high = upscale_range
        controls.append(io.Float.Input("upscale_factor", display_name="upscale factor", default=low, min=low, max=high))
    if creativity is not None:
        low, high = creativity
        controls.append(io.Float.Input("creativity", default=low, min=low, max=high, step=0.05))
    return controls


def _define_children(choice: VideoChoice) -> list[io.Input]:
    """Show only the durations, sizes, sound, frames, and references this model accepts.

    A list with one value offers no choice, so it is left out and the model uses that value.
    """
    children: list[io.Input] = []
    if len(choice.durations) > 1:
        durations = [str(duration) for duration in sorted(choice.durations)]
        # Video is priced per second, so the shortest duration comes first.
        children.append(
            io.Combo.Input("duration", options=durations, default=durations[0], tooltip="The length in seconds.")
        )
    for field, values in (("resolution", choice.resolutions), ("aspect_ratio", choice.aspect_ratios)):
        if len(values) > 1:
            options = [MODEL_DEFAULT, *values]
            children.append(
                io.Combo.Input(field, display_name=field.replace("_", " "), options=options, default=MODEL_DEFAULT)
            )
    if choice.generate_audio is not None:
        children.append(
            io.Boolean.Input("generate_audio", display_name="generate audio", default=choice.generate_audio)
        )
    return [
        *children,
        *_define_media(choice.frame_types, choice.reference_types),
        *_define_upscale(choice.upscale_range, choice.creativity_range),
    ]


def _encode_frames(model: Mapping[str, object]) -> dict[str, str]:
    """Encode each connected frame, refusing a batch, since a frame is one image."""
    frames: dict[str, str] = {}
    for frame in ("first_frame", "last_frame"):
        image = model.get(frame)
        if not isinstance(image, torch.Tensor):
            continue
        if image.shape[0] != 1:
            raise ConnectorError(ErrorCode.INVALID_INPUT, IMAGE_BATCH)
        frames[frame] = encode_images(image)[0]
    return frames


def _encode_references(model: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    """Encode every connected reference image, video, and audio clip as a (kind, data URL) pair."""
    references: list[tuple[str, str]] = []
    for kind, socket in (("image", "reference_images"), ("video", "reference_videos"), ("audio", "reference_audio")):
        slots = cast("Mapping[str, object]", model.get(socket) or {})
        for _name, value in sorted(slots.items(), key=lambda item: int(item[0].rsplit("_", 1)[1])):
            if isinstance(value, torch.Tensor):
                references += [(kind, url) for url in encode_images(value)]
            elif isinstance(value, Input.Video):
                references.append((kind, f"data:video/mp4;base64,{encode_video(value)}"))
            elif value is not None:
                references.append((kind, f"data:audio/wav;base64,{encode_audio(cast('Input.Audio', value))}"))
    return tuple(references)


class VideoGenerate(PaidNode):
    """Submit one video job, record it, wait for it, and return the video."""

    contract: ClassVar[str] = "video-generate-v1"

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Build the model dropdown, one option per video model, with every control a written ID may use."""
        written = [
            io.Int.Input(
                "duration",
                default=DEFAULT_DURATION,
                min=0,
                max=DURATION_RANGE[1],
                tooltip="The length in seconds; 0 leaves it to the model.",
            ),
            io.Combo.Input("resolution", options=list(ALL_RESOLUTIONS), default=MODEL_DEFAULT),
            io.Combo.Input(
                "aspect_ratio", display_name="aspect ratio", options=list(ALL_ASPECT_RATIOS), default=MODEL_DEFAULT
            ),
            io.Combo.Input(
                "generate_audio", display_name="generate audio", options=list(AUDIO_CHOICES), default=MODEL_DEFAULT
            ),
            *_define_media(("first_frame", "last_frame"), frozenset({"image", "video", "audio"})),
        ]
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
                define_model_input("videos", DEFAULT_VIDEO_MODEL, _define_children, written),
                *define_request_inputs(has_seed=True),
            ],
            outputs=[io.Video.Output("video", display_name="video")],
        )

    @classmethod
    async def send(
        cls, *, prompt: str, model: dict[str, object], seed: int, options: RequestOptions | None = None
    ) -> io.NodeOutput:
        """Encode the frames and references inside the owned task, then submit, record, and wait."""
        selection = read_model("videos", model, VideoChoice)
        duration = cast("str | int | None", model.get("duration"))
        sound = model.get("generate_audio")
        # A dropdown left at the model's default sends nothing.
        chosen = {
            field: str(model[field])
            for field in ("resolution", "aspect_ratio")
            if model.get(field, MODEL_DEFAULT) != MODEL_DEFAULT
        }

        async def start() -> io.NodeOutput:
            """Encode the media inside the owned task, then send the request."""
            frames, references = await owned_io(lambda: (_encode_frames(model), _encode_references(model)))
            request = VideoRequest(
                model_id=selection.model_id,
                choice=selection.choice,
                prompt=prompt,
                duration=int(duration) if duration else None,
                resolution=chosen.get("resolution"),
                aspect_ratio=chosen.get("aspect_ratio"),
                frame_urls=frames,
                references=references,
                generate_audio=sound if isinstance(sound, bool) else {"on": True, "off": False}.get(str(sound)),
                seed=seed,
                upscale_factor=cast("float | None", model.get("upscale_factor")),
                creativity=cast("float | None", model.get("creativity")),
                options=options,
            )
            # ComfyUI reads the MP4 from memory, so no temporary file is written.
            return await run_request(
                VideoOperation(request, get_runtime().jobs),
                lambda content: io.NodeOutput(InputImpl.VideoFromFile(memory.BytesIO(content))),
            )

        return await wait_for_execution(asyncio.create_task(start()))


__all__ = ["VideoGenerate"]
