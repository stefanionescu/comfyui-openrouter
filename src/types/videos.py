"""Video requests and the job records kept while OpenRouter makes a video."""

from __future__ import annotations

from . import Value
from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from .options import RequestOptions
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
    options: RequestOptions | None


class VideoJob(Value):
    """One video job recorded as soon as OpenRouter accepts it, or one uncertain submission.

    Attributes:
        version: File format version.
        name: The record's file stem: the job ID, or uncertain- and the request hash.
        job_id: OpenRouter's job ID, or None for an uncertain submission.
        model_id: The model the job runs on.
        request_hash: SHA-256 of the complete request body, so only an identical request matches.
        submitted_at: When the request was sent, in ISO 8601.
        status: accepted once OpenRouter answered, uncertain when the connection closed first.

    """

    version: Literal[1]
    name: str
    job_id: str | None
    model_id: str
    request_hash: str
    submitted_at: str
    status: Literal["accepted", "uncertain"]


__all__ = ["VideoJob", "VideoRequest"]
