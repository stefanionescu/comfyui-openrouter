"""Submit a video job, record it as soon as OpenRouter accepts it, wait for it, and download the video."""

from __future__ import annotations

import re
import json
import math
import time
import asyncio
import hashlib
from typing import TYPE_CHECKING
from datetime import UTC, datetime
from ..models import validate_model
from ...types.videos import VideoJob
from pydantic import ValidationError
from ..failures import sanitize_reason
from ..options import build_request_body
from ...types.replies import VideoJobReply
from ..operation import validate_upload_size
from ...config.patterns import JOB_ID_PATTERN
from ..transport import download_video, send_json
from ...types.errors import ErrorCode, OpenRouterError
from ...config.openrouter import VIDEOS_URL, VIDEO_JOB_URL
from ...config.messages.run import REPLY_EMPTY, REPLY_UNREADABLE
from ...config.generation.videos import DONE_STATUSES, UNCERTAIN_PREFIX, SECONDS_PER_MINUTE
from ...config.generation.videos import MAX_REFERENCE_AUDIO, MAX_REFERENCE_IMAGES, MAX_REFERENCE_VIDEOS
from ...config.messages.videos import (
    JOB_FAILED,
    JOB_EXPIRED,
    SUBMIT_HOLD,
    JOB_CANCELLED,
    JOB_WAIT_LIMIT,
    PROMPT_REQUIRED,
    SUBMIT_UNCERTAIN,
    VIDEO_REFERENCES_RANGE,
    FRAMES_BESIDE_REFERENCES,
)

if TYPE_CHECKING:
    from ...types import Json
    from .jobs import JobStore
    from ...types.videos import VideoRequest
    from ...types.settings import Settings, Configuration

JOB_ID = re.compile(JOB_ID_PATTERN)
REFERENCE_LIMITS = {"image": MAX_REFERENCE_IMAGES, "video": MAX_REFERENCE_VIDEOS, "audio": MAX_REFERENCE_AUDIO}


class VideoDownloadOperation:
    """Wait for one recorded job and download its video; status and download requests bill nothing."""

    def __init__(self, job: VideoJob, jobs: JobStore) -> None:
        """Keep the recorded job and the store that removes its record once it ends."""
        self.job = job
        self.jobs = jobs

    def validate(self, settings: Settings) -> None:
        """Accept any recorded job; there is nothing to refuse before checking its status."""

    async def send(self, configuration: Configuration) -> bytes:
        """Check the job at once, so a job that finished while ComfyUI was closed downloads immediately.

        A cancel or the wait limit leaves the record in place, which is what lets Video: Download finish it.
        """
        settings = configuration.settings
        deadline = time.monotonic() + settings.video_wait_minutes * SECONDS_PER_MINUTE
        while True:
            content = await download_video(VIDEO_JOB_URL.format(job_id=self.job.job_id), configuration)
            try:
                reply = VideoJobReply.model_validate_json(content)
            except ValidationError:
                raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
            if reply.status in DONE_STATUSES:
                break
            if time.monotonic() >= deadline:
                raise OpenRouterError(ErrorCode.TIMEOUT, JOB_WAIT_LIMIT.format(minutes=settings.video_wait_minutes))
            await asyncio.sleep(settings.video_poll_seconds)
        if reply.status != "completed":
            await asyncio.to_thread(self.jobs.delete, self.job.name)
            reason = sanitize_reason(reply.error or "")
            ended = {"failed": JOB_FAILED, "cancelled": JOB_CANCELLED}.get(reply.status, JOB_EXPIRED)
            raise OpenRouterError(ErrorCode.UNAVAILABLE, ended.format(reason=reason))
        if not reply.unsigned_urls:
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_EMPTY)
        video = await download_video(reply.unsigned_urls[0], configuration)
        # The record goes only after the download, so a failed download can be collected again.
        await asyncio.to_thread(self.jobs.delete, self.job.name)
        return video


class VideoOperation:
    """One video job, resumed instead of sent again when an identical one is already running."""

    def __init__(self, request: VideoRequest, jobs: JobStore) -> None:
        """Keep the request to validate and send, and the store its job is recorded in."""
        self.request = request
        self.jobs = jobs

    def validate(self, settings: Settings) -> None:
        """Refuse a request with nothing to animate, frames beside references, and too much media."""
        request = self.request
        if not request.prompt.strip() and "first_frame" not in request.frame_urls:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, PROMPT_REQUIRED)
        if request.frame_urls and request.references:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, FRAMES_BESIDE_REFERENCES)
        validate_upload_size((*request.frame_urls.values(), *(url for _kind, url in request.references)), settings)
        for kind, limit in REFERENCE_LIMITS.items():
            if sum(item == kind for item, _url in request.references) > limit:
                raise OpenRouterError(ErrorCode.INVALID_INPUT, VIDEO_REFERENCES_RANGE.format(maximum=limit, kind=kind))

    def build_body(self, parameters: frozenset[str]) -> dict[str, Json]:
        """Build the job request, sending each control only when set and the seed only when the model takes it."""
        request = self.request
        body: dict[str, Json] = {"model": request.model_id, "prompt": request.prompt}
        chosen: dict[str, Json] = {
            "duration": request.duration,
            "resolution": request.resolution,
            "aspect_ratio": request.aspect_ratio,
            "generate_audio": request.generate_audio,
            "upscale_factor": request.upscale_factor,
            "creativity": request.creativity,
        }
        body.update({field: value for field, value in chosen.items() if value is not None})
        if "seed" in parameters:
            body["seed"] = request.seed
        if request.frame_urls:
            body["frame_images"] = [
                {"type": "image_url", "image_url": {"url": url}, "frame_type": frame}
                for frame, url in request.frame_urls.items()
            ]
        if request.references:
            body["input_references"] = [
                {"type": f"{kind}_url", f"{kind}_url": {"url": url}} for kind, url in request.references
            ]
        return build_request_body(body, request.options, "videos")

    async def send(self, configuration: Configuration) -> bytes:
        """Resume an identical recorded job instead of paying for a second one, or submit and record a new job."""
        settings = configuration.settings
        model = await validate_model(self.request.model_id, "videos", configuration)
        body = self.build_body(model.parameters)
        request_hash = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        found = await asyncio.to_thread(self.jobs.find, request_hash, settings.resubmit_hold_minutes)
        if found is not None and found.status == "accepted":
            return await VideoDownloadOperation(found, self.jobs).send(configuration)
        if found is not None:
            elapsed = (datetime.now(UTC) - datetime.fromisoformat(found.submitted_at)).total_seconds()
            minutes = max(1, math.ceil(settings.resubmit_hold_minutes - elapsed / SECONDS_PER_MINUTE))
            raise OpenRouterError(ErrorCode.UNCERTAIN, SUBMIT_HOLD.format(minutes=minutes))
        job = VideoJob(
            version=1,
            name=UNCERTAIN_PREFIX + request_hash,
            job_id=None,
            model_id=self.request.model_id,
            request_hash=request_hash,
            submitted_at=datetime.now(UTC).isoformat(),
            status="uncertain",
        )
        try:
            document = await send_json(VIDEOS_URL, body, configuration)
        except OpenRouterError as error:
            # The request may have been accepted and billed, so an identical one is held back for a while.
            if error.code not in {ErrorCode.UNCERTAIN, ErrorCode.TIMEOUT}:
                raise
            await asyncio.to_thread(self.jobs.save, job)
            raise OpenRouterError(
                ErrorCode.UNCERTAIN, SUBMIT_UNCERTAIN.format(minutes=settings.resubmit_hold_minutes)
            ) from None
        try:
            reply = VideoJobReply.model_validate(document)
        except ValidationError:
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        if JOB_ID.match(reply.id) is None:
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
        # The record is written before the first wait, so a cancel one moment later still leaves it.
        accepted = job.model_copy(update={"name": reply.id, "job_id": reply.id, "status": "accepted"})
        await asyncio.to_thread(self.jobs.save, accepted)
        return await VideoDownloadOperation(accepted, self.jobs).send(configuration)


__all__ = ["VideoDownloadOperation", "VideoOperation"]
