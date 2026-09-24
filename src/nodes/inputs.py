"""Build the inputs the paid nodes share, the seed, the run number, and the options, and encode their media lists."""

from __future__ import annotations

from typing import TYPE_CHECKING
from comfy_api.latest import io, Input
from ..config.media import MP4_URL_PREFIX
from ..config.namespace import OPTIONS_TYPE
from ..comfy.media import encode_audio, encode_video, encode_images
from ..config.generation.inputs import (
    MAX_SEED,
    SEED_INPUT,
    DEFAULT_SEED,
    OPTIONS_INPUT,
    MAX_RUN_NUMBER,
    MIN_RUN_NUMBER,
    RUN_NUMBER_INPUT,
    DEFAULT_RUN_NUMBER,
)

if TYPE_CHECKING:
    import torch
    from collections.abc import Sequence


def build_request_inputs(*, has_seed: bool) -> list[io.Input]:
    """Build the seed, run number, and options inputs that follow a paid node's own inputs."""
    seed = io.Int.Input(
        SEED_INPUT,
        display_name="seed",
        tooltip="Number used by the model to vary its output. Results can change after model updates.",
        default=DEFAULT_SEED,
        min=0,
        max=MAX_SEED,
        control_after_generate=True,
    )
    run_number = io.Int.Input(
        RUN_NUMBER_INPUT,
        display_name="run number",
        tooltip="Change this number to send the same request again" + (" with the same seed." if has_seed else "."),
        default=DEFAULT_RUN_NUMBER,
        min=MIN_RUN_NUMBER,
        max=MAX_RUN_NUMBER,
    )
    options = io.Custom(OPTIONS_TYPE).Input(
        OPTIONS_INPUT,
        optional=True,
        tooltip="Connect Request Options to choose providers or pass extra fields.",
    )
    return [seed, run_number, options] if has_seed else [run_number, options]


def encode_media(
    images: Sequence[torch.Tensor] | None, videos: Sequence[Input.Video] | None, audio: Sequence[Input.Audio] | None
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Encode every image, video, and audio clip that reached the list sockets, in order.

    Every image of a batch becomes a PNG data URL and every clip of an audio batch a base64 WAV; videos are MP4 data
    URLs.
    """
    clips = [
        Input.Audio(waveform=clip["waveform"][index : index + 1], sample_rate=clip["sample_rate"])
        for clip in audio or ()
        for index in range(clip["waveform"].shape[0])
    ]
    image_urls = tuple(url for batch in images or () for url in encode_images(batch))
    video_urls = tuple(MP4_URL_PREFIX + encode_video(video) for video in videos or ())
    return image_urls, video_urls, tuple(encode_audio(clip) for clip in clips)


__all__ = ["build_request_inputs", "encode_media"]
