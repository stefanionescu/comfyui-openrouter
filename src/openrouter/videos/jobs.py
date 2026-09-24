"""Keep a private record of every video job OpenRouter accepted, and of every uncertain submission.

Video jobs keep running and billing after the extension stops waiting, because OpenRouter has no cancel
endpoint, so the records let no paid video be lost and no identical video be paid for twice.
"""

from __future__ import annotations

import re
import threading
from typing import TYPE_CHECKING
from datetime import UTC, datetime
from ...types.videos import VideoJob
from pydantic import ValidationError
from ...config.patterns import JOB_ID_PATTERN
from ...config.units import SECONDS_PER_MINUTE
from ...config.messages.videos import JOB_UNKNOWN
from ...storage.files import save_file, read_file
from ...types.errors import ErrorCode, OpenRouterError
from ...config.storage import JOB_FILE_SUFFIX, MAX_LISTED_JOBS, MAX_JOB_FILE_BYTES

if TYPE_CHECKING:
    from pathlib import Path

JOB_ID = re.compile(JOB_ID_PATTERN)


class JobStore:
    """Own the job records folder; every method blocks, so callers run it off the event loop."""

    def __init__(self, directory: Path) -> None:
        """Select the private jobs folder and the lock its files share across threads."""
        self.directory = directory
        self._lock = threading.Lock()

    def _read_all(self) -> list[VideoJob]:
        """Read every record; a damaged or oversized file is skipped, so it never blocks the other jobs."""
        if not self.directory.is_dir():
            return []
        jobs: list[VideoJob] = []
        for path in sorted(self.directory.glob(f"*{JOB_FILE_SUFFIX}")):
            try:
                jobs.append(VideoJob.model_validate_json(read_file(path, max_bytes=MAX_JOB_FILE_BYTES)))
            except (OSError, ValidationError, OpenRouterError):
                continue
        return jobs

    def save(self, job: VideoJob) -> None:
        """Write one record atomically, named by its job ID or its uncertain request hash."""
        path = self.directory / f"{job.name}{JOB_FILE_SUFFIX}"
        with self._lock:
            save_file(path, (job.model_dump_json(indent=2) + "\n").encode())

    def delete(self, name: str) -> None:
        """Delete one record; a record already gone needs no removal."""
        path = self.directory / f"{name}{JOB_FILE_SUFFIX}"
        with self._lock:
            # reason: Record names are validated job IDs or request hashes inside the private jobs folder.
            # bearer:disable python_lang_path_traversal
            path.unlink(missing_ok=True)

    def find(self, request_hash: str, hold_minutes: int) -> VideoJob | None:
        """Return the accepted job for an identical request, or an uncertain one still within its hold.

        An uncertain record older than the hold is deleted, so the identical request may be sent again.
        """
        now = datetime.now(UTC)
        with self._lock:
            for job in self._read_all():
                if job.request_hash != request_hash:
                    continue
                if job.status == "accepted":
                    return job
                age = (now - datetime.fromisoformat(job.submitted_at)).total_seconds()
                if age < hold_minutes * SECONDS_PER_MINUTE:
                    return job
                (self.directory / f"{job.name}{JOB_FILE_SUFFIX}").unlink(missing_ok=True)
        return None

    def list_accepted(self) -> list[VideoJob]:
        """List the accepted jobs, newest first."""
        with self._lock:
            jobs = [job for job in self._read_all() if job.status == "accepted"]
        return sorted(jobs, key=lambda job: job.submitted_at, reverse=True)[:MAX_LISTED_JOBS]

    def read(self, job_id: str) -> VideoJob:
        """Return the accepted job with this ID."""
        with self._lock:
            job = next((job for job in self._read_all() if job.job_id == job_id and JOB_ID.match(job_id)), None)
        if job is None or job.status != "accepted":
            raise OpenRouterError(ErrorCode.INVALID_INPUT, JOB_UNKNOWN)
        return job


__all__ = ["JobStore"]
