"""Execution settings and private configuration snapshot records."""

import json
import hashlib
from .credentials import Credential
from dataclasses import field, asdict, dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Limits that a workflow cannot raise.

    Attributes:
        request_timeout_seconds: Total time one paid request may take.
        max_upload_megabytes: Largest encoded media in one request.
        max_download_megabytes: Largest reply body, image, audio, or video accepted.
        parallel_requests: Requests in flight at once per ComfyUI run.
        video_poll_seconds: Time between video status checks.
        video_wait_minutes: How long one run waits for a video job.
        resubmit_hold_minutes: How long an uncertain video request blocks an identical one.

    """

    request_timeout_seconds: int
    max_upload_megabytes: int
    max_download_megabytes: int
    parallel_requests: int
    video_poll_seconds: int
    video_wait_minutes: int
    resubmit_hold_minutes: int

    @property
    def revision(self) -> str:
        """Identify these non-secret settings so a stale window cannot overwrite newer changes."""
        encoded = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class ExecutionConfiguration:
    """One private settings and credential snapshot for one paid request.

    Attributes:
        settings: Effective execution limits.
        credential: Private OpenRouter key excluded from representations.
        generation: Token identifying the effective execution configuration.

    """

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str


__all__ = ["ExecutionConfiguration", "Settings"]
