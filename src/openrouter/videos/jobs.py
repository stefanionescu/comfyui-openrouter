"""Keep a private record of every video job OpenRouter accepted.

Video jobs keep running and billing after the extension stops waiting, because OpenRouter has no cancel
endpoint, so the records let no paid video be lost.
"""

from __future__ import annotations

import re
import threading
from typing import TYPE_CHECKING
from ...types.videos import VideoJob
from pydantic import ValidationError
from ...config.patterns import JOB_ID_PATTERN
from ...config.messages.videos import JOB_UNKNOWN
from ...storage.files import save_file, read_file
from ...types.errors import ErrorCode, OpenRouterError
from ...config.storage import JOB_FILES, MAX_FILE_BYTES

if TYPE_CHECKING:
    from pathlib import Path

# A job ID in OpenRouter's documented format, which is also safe as a record's file name.
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
        for path in sorted(self.directory.glob(f"*{JOB_FILES['SUFFIX']}")):
            try:
                jobs.append(VideoJob.model_validate_json(read_file(path, max_bytes=MAX_FILE_BYTES["JOB"])))
            except (OSError, ValidationError, OpenRouterError):
                continue
        return jobs

    def save(self, job: VideoJob) -> None:
        """Write one record atomically, named by its job ID."""
        path = self.directory / f"{job.job_id}{JOB_FILES['SUFFIX']}"
        with self._lock:
            save_file(path, (job.model_dump_json(indent=2) + "\n").encode())

    def delete(self, job_id: str) -> None:
        """Delete one record; a record already gone needs no removal."""
        path = self.directory / f"{job_id}{JOB_FILES['SUFFIX']}"
        with self._lock:
            # reason: Record names are validated job IDs inside the private jobs folder.
            # bearer:disable python_lang_path_traversal
            path.unlink(missing_ok=True)

    def list_jobs(self) -> list[VideoJob]:
        """List the recorded jobs, newest first."""
        with self._lock:
            jobs = self._read_all()
        return sorted(jobs, key=lambda job: job.submitted_at, reverse=True)

    def read(self, job_id: str) -> VideoJob:
        """Return the recorded job with this ID."""
        with self._lock:
            job = next((job for job in self._read_all() if job.job_id == job_id and JOB_ID.match(job_id)), None)
        if job is None:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, JOB_UNKNOWN)
        return job


__all__ = ["JOB_ID", "JobStore"]
