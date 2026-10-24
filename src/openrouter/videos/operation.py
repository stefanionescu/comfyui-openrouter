"""Submit a video job, record it as soon as OpenRouter accepts it, wait for it, and download the video."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
import asyncio
from datetime import UTC, datetime
from dataclasses import dataclass

from pydantic import ValidationError

from .jobs import JOB_ID
from ..models import validate_model, validate_limits, read_video_limits
from ..options import build_request_body
from ..failures import sanitize_reason
from ..operation import validate_upload_size
from ..transport import download, send_json
from ...state.errors import ErrorCode, OpenRouterError
from ...state.videos import VideoJob
from ...state.replies import VideoJobReply
from ...config.openrouter import ENDPOINT_URLS, VIDEO_JOB_URLS
from ...config.messages.run import REPLY_UNREADABLE
from ...config.messages.models import MODEL_FRAME
from ...config.messages.videos import (
    JOB_FAILED,
    JOB_EXPIRED,
    JOB_CANCELLED,
    JOB_WAIT_LIMIT,
    PROMPT_REQUIRED,
    FRAMES_BESIDE_REFERENCES,
)
from ...config.generation.videos import DONE_STATUSES, POLL_INTERVAL_SECONDS

if TYPE_CHECKING:
    from .jobs import JobStore
    from ...state import Json
    from ...state.models import Model, Limits
    from ...state.videos import VideoRequest
    from ...state.settings import Settings, Configuration


def _read_job_id(document: Json) -> str:
    """Read the ID of the job OpenRouter accepted.

    The reply came with a success status, so a job may be running and billing even when its ID is unreadable.
    """
    try:
        reply = VideoJobReply.model_validate(document)
    except ValidationError:
        raise OpenRouterError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE) from None
    if JOB_ID.match(reply.id) is None:
        raise OpenRouterError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE)
    return reply.id


@dataclass(frozen=True, slots=True)
class VideoDownloadOperation:
    """Wait for one recorded job and download its video; status and download requests bill nothing.

    The operation accepts any recorded job; there is nothing to refuse before checking its status.

    Attributes:
        job: The recorded job.
        jobs: The store that removes its record once it ends.

    """

    job: VideoJob
    jobs: JobStore

    async def send(self, configuration: Configuration) -> bytes:
        """Check the job at once, so a job that finished while ComfyUI was not running downloads immediately.

        A cancel or the request timeout leaves the record in place, which is what lets Video: Download finish it.
        """
        settings = configuration.settings
        deadline = time.monotonic() + settings.request_timeout_seconds
        while True:
            status_url = VIDEO_JOB_URLS['STATUS'].format(job_id=self.job.job_id)
            content = await download(status_url, configuration.settings, credential=configuration.credential)
            try:
                reply = VideoJobReply.model_validate_json(content)
            except ValidationError:
                raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
            if reply.status in DONE_STATUSES:
                break
            if time.monotonic() >= deadline:
                raise OpenRouterError(
                    ErrorCode.TIMEOUT, JOB_WAIT_LIMIT.format(seconds=settings.request_timeout_seconds)
                )
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
        if reply.status != 'completed':
            await asyncio.to_thread(self.jobs.delete, self.job.job_id)
            reason = sanitize_reason(reply.error or '')
            ended = {'failed': JOB_FAILED, 'cancelled': JOB_CANCELLED}.get(reply.status, JOB_EXPIRED)
            raise OpenRouterError(ErrorCode.UNAVAILABLE, ended.format(reason=reason))
        content_url = VIDEO_JOB_URLS['CONTENT'].format(job_id=self.job.job_id)
        video = await download(content_url, configuration.settings, credential=configuration.credential)
        # The record goes only after the download, so a later run can collect a failed download again.
        await asyncio.to_thread(self.jobs.delete, self.job.job_id)
        return video


@dataclass(frozen=True, slots=True)
class VideoOperation:
    """One video job, sent once and recorded as soon as OpenRouter accepts it.

    Attributes:
        request: The request to validate and send.
        jobs: The store that records its job.

    """

    request: VideoRequest
    jobs: JobStore

    async def _read_model(self, configuration: Configuration) -> tuple[Model, Limits | None]:
        """Check that the model reads the connected media, and read its entry in OpenRouter's video list."""
        request = self.request
        kinds = {kind for kind, _url in request.references}
        if request.frame_urls:
            kinds.add('image')
        model = await validate_model(request.model_id, 'videos', configuration.settings, sorted(kinds))
        return model, await read_video_limits(request.model_id, model.parameters, configuration.settings)

    def validate(self, settings: Settings) -> None:
        """Refuse a request with nothing to animate, frames beside references, and media over the upload limit."""
        request = self.request
        if not request.prompt.strip() and 'first_frame' not in request.frame_urls:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, PROMPT_REQUIRED)
        if request.frame_urls and request.references:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, FRAMES_BESIDE_REFERENCES)
        validate_upload_size((*request.frame_urls.values(), *(url for _kind, url in request.references)), settings)

    def build_body(self, parameters: frozenset[str], limits: Limits | None) -> dict[str, Json]:
        """Build the job request, checked against the model's entry in OpenRouter's video list when it has one.

        Each control goes only when set, the seed only to a model that takes it, and sound turned off stays out for a
        model that makes none.
        """
        request = self.request
        values: dict[str, Json] = {
            'duration': request.duration,
            'resolution': request.resolution,
            'aspect_ratio': request.aspect_ratio,
            'generate_audio': request.generate_audio,
            'upscale_factor': request.upscale_factor,
            'creativity': request.creativity,
        }
        chosen = {field: value for field, value in values.items() if value is not None}
        if limits is not None:
            if request.generate_audio is False and 'generate_audio' not in limits.fields:
                del chosen['generate_audio']
            for frame in request.frame_urls:
                if frame not in limits.fields:
                    message = MODEL_FRAME.format(model=request.model_id, frame=frame)
                    raise OpenRouterError(ErrorCode.INVALID_INPUT, message)
            validate_limits(request.model_id, limits, chosen)
        body: dict[str, Json] = {'model': request.model_id, 'prompt': request.prompt, **chosen}
        if 'seed' in (limits.fields if limits is not None else parameters):
            body['seed'] = request.seed
        if request.frame_urls:
            body['frame_images'] = [
                {'type': 'image_url', 'image_url': {'url': url}, 'frame_type': frame}
                for frame, url in request.frame_urls.items()
            ]
        if request.references:
            body['input_references'] = [
                {'type': f'{kind}_url', f'{kind}_url': {'url': url}} for kind, url in request.references
            ]
        return build_request_body(body, request.options, 'videos')

    async def send(self, configuration: Configuration) -> bytes:
        """Submit the job, record it as soon as OpenRouter accepts it, and wait for its video."""
        model, limits = await self._read_model(configuration)
        body = self.build_body(model.parameters, limits)
        submitted_at = datetime.now(UTC).isoformat()
        job_id = _read_job_id(await send_json(ENDPOINT_URLS['videos'], body, configuration))
        # The operation writes the record before the first wait, so a cancel one moment later still leaves it.
        job = VideoJob(version=1, job_id=job_id, model_id=self.request.model_id, submitted_at=submitted_at)
        await asyncio.to_thread(self.jobs.save, job)
        return await VideoDownloadOperation(job, self.jobs).send(configuration)


__all__ = ['VideoDownloadOperation', 'VideoOperation']
