"""Video requests and the job records kept while OpenRouter makes a video."""

from __future__ import annotations

from . import Value
from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from .options import Options
    from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class VideoRequest:
    """One video job request, with its media already encoded.

    Attributes:
        model_id: The model ID sent to OpenRouter.
        prompt: What the video shows.
        duration: Seconds, or None for the model's default.
        resolution: Resolution, or None for the model's default.
        aspect_ratio: Aspect ratio, or None for the model's default.
        frame_urls: PNG data URLs keyed first_frame or last_frame.
        references: (kind, data URL) pairs, where kind is image, video, or audio.
        generate_audio: Whether to make sound, or None to send nothing.
        seed: Seed sent when the model accepts one.
        upscale_factor: Upscale factor of an upscaling model, or None.
        creativity: Creativity of an upscaling model, or None.
        options: Provider routing and extra fields.

    """

    model_id: str
    prompt: str
    duration: int | None
    resolution: str | None
    aspect_ratio: str | None
    frame_urls: Mapping[str, str]
    references: tuple[tuple[str, str], ...]
    generate_audio: bool | None
    seed: int
    upscale_factor: float | None
    creativity: float | None
    options: Options | None


class VideoJob(Value):
    """One video job, recorded as soon as OpenRouter accepts it.

    Attributes:
        version: File format version.
        job_id: OpenRouter's job ID, which also names the record's file.
        model_id: The model the job runs on.
        submitted_at: When the request was sent, in ISO 8601.

    """

    version: Literal[1]
    job_id: str
    model_id: str
    submitted_at: str


__all__ = ["VideoJob", "VideoRequest"]
