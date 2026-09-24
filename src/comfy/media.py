"""Check ComfyUI media, then convert it with ComfyUI's own helpers to what OpenRouter sends and reads.

Encoding and decoding block, so callers run these functions through owned_io.
"""

from __future__ import annotations

import io
import wave
import torch
from comfy_api.latest import Types
from typing import cast, TYPE_CHECKING
from ..types.errors import ErrorCode, OpenRouterError
from ..config.media import (
    WAV_CODEC,
    WAV_FORMAT,
    RGB_CHANNELS,
    RGBA_CHANNELS,
    MAX_IMAGE_SIDE,
    IMAGE_DIMENSIONS,
    WAV_SAMPLE_BYTES,
)
from ..config.messages.media import (
    IMAGE_SIZE,
    AUDIO_BATCH,
    AUDIO_EMPTY,
    IMAGE_SHAPE,
    IMAGE_PIXELS,
    AUDIO_UNREADABLE,
    AUDIO_UNWRITABLE,
    IMAGE_UNREADABLE,
    VIDEO_UNREADABLE,
)
from comfy_api_nodes.util.conversions import (
    tensor_to_data_uri,
    audio_to_base64_string,
    video_to_base64_string,
    bytesio_to_image_tensor,
    audio_bytes_to_audio_input,  # pyright: ignore[reportUnknownVariableType] -- reason: ComfyUI annotates the result as a bare dict.
)

if TYPE_CHECKING:
    from comfy_api.latest import Input


def encode_images(image: torch.Tensor) -> tuple[str, ...]:
    """Send every image of a batch as a PNG data URL, never shrinking it; the size limits refuse large images."""
    if image.ndim != IMAGE_DIMENSIONS or image.shape[-1] not in {RGB_CHANNELS, RGBA_CHANNELS}:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, IMAGE_SHAPE)
    if max(image.shape[1], image.shape[2]) > MAX_IMAGE_SIDE:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, IMAGE_SIZE.format(maximum=MAX_IMAGE_SIDE))
    if not bool(torch.isfinite(image).all()):
        raise OpenRouterError(ErrorCode.INVALID_INPUT, IMAGE_PIXELS)
    try:
        return tuple(tensor_to_data_uri(frame.clamp(0, 1), total_pixels=None) for frame in image)
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise OpenRouterError(ErrorCode.MEDIA, IMAGE_SHAPE) from None


def decode_image(content: bytes) -> tuple[torch.Tensor, torch.Tensor]:
    """Read one image as pixels [1, H, W, 3] and its mask [1, H, W], where the mask is 1 minus alpha."""
    try:
        pixels = bytesio_to_image_tensor(io.BytesIO(content))
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise OpenRouterError(ErrorCode.MEDIA, IMAGE_UNREADABLE) from None
    if pixels.shape[-1] == RGBA_CHANNELS:
        return pixels[..., :RGB_CHANNELS].contiguous(), 1.0 - pixels[..., RGB_CHANNELS]
    return pixels, torch.zeros(pixels.shape[:3], dtype=pixels.dtype)


def encode_audio(audio: Input.Audio) -> str:
    """Send one audio clip as base64 WAV without a data: prefix."""
    waveform = audio["waveform"]
    if waveform.shape[0] != 1:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, AUDIO_BATCH)
    if waveform.shape[-1] == 0:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, AUDIO_EMPTY)
    try:
        return audio_to_base64_string(audio, container_format=WAV_FORMAT, codec_name=WAV_CODEC)
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise OpenRouterError(ErrorCode.MEDIA, AUDIO_UNWRITABLE) from None


def decode_audio(content: bytes) -> dict[str, object]:
    """Read an encoded audio file, such as MP3 or WAV, as ComfyUI audio."""
    try:
        return cast("dict[str, object]", audio_bytes_to_audio_input(content))
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise OpenRouterError(ErrorCode.MEDIA, AUDIO_UNREADABLE) from None


def decode_pcm(content: bytes, sample_rate: int, channels: int) -> dict[str, object]:
    """Read raw 16-bit PCM as ComfyUI audio by giving it the WAV header it lacks."""
    # Raw PCM has no header, so a length that splits a sample means the reply is not the PCM it claims.
    if not content or len(content) % (WAV_SAMPLE_BYTES * channels):
        raise OpenRouterError(ErrorCode.MEDIA, AUDIO_UNREADABLE)
    container = io.BytesIO()
    with wave.open(container, "wb") as stream:
        stream.setnchannels(channels)
        stream.setsampwidth(WAV_SAMPLE_BYTES)
        stream.setframerate(sample_rate)
        stream.writeframes(content)
    return decode_audio(container.getvalue())


def encode_video(video: Input.Video) -> str:
    """Send a ComfyUI video as base64 H.264 MP4."""
    try:
        return video_to_base64_string(video, Types.VideoContainer.MP4, Types.VideoCodec.H264)
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise OpenRouterError(ErrorCode.MEDIA, VIDEO_UNREADABLE) from None


__all__ = ["decode_audio", "decode_image", "decode_pcm", "encode_audio", "encode_images", "encode_video"]
