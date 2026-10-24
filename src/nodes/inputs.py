"""Encode the media lists that reach the paid nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from comfy_api.latest import Input

from ..comfy.media import encode_audio, encode_video, encode_images
from ..config.media import VIDEO_URL_PREFIX

if TYPE_CHECKING:
    from collections.abc import Sequence

    import torch


def encode_media(
    images: Sequence[torch.Tensor] | None, videos: Sequence[Input.Video] | None, audio: Sequence[Input.Audio] | None
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Encode every image, video, and audio clip that reached the list sockets, in order.

    Every image of a batch becomes a lossless WebP data URL and every clip of an audio batch a base64 WAV; videos are
    MP4 data URLs.
    """
    clips = [
        Input.Audio(waveform=clip['waveform'][index : index + 1], sample_rate=clip['sample_rate'])
        for clip in audio or ()
        for index in range(clip['waveform'].shape[0])
    ]
    image_urls = tuple(url for batch in images or () for url in encode_images(batch))
    video_urls = tuple(VIDEO_URL_PREFIX + encode_video(video) for video in videos or ())
    return image_urls, video_urls, tuple(encode_audio(clip) for clip in clips)


__all__ = ['encode_media']
