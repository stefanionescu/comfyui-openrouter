"""Keep a private record of every video job OpenRouter accepted.

Video jobs keep running and billing after the extension stops waiting, because OpenRouter has no cancel
endpoint, so the records keep track of every paid video.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
import threading
from dataclasses import field, dataclass

from pydantic import ValidationError

from ...state.errors import ErrorCode, OpenRouterError
from ...state.videos import VideoJob
from ...storage.files import read_file, save_file
from ...config.storage import JOB_FILES, MAX_FILE_BYTES
from ...config.patterns import JOB_ID_PATTERN
from ...config.messages.videos import JOB_UNKNOWN

if TYPE_CHECKING:
    from pathlib import Path

# A job ID in OpenRouter's documented format, which is also safe as a record's file name.
JOB_ID = re.compile(JOB_ID_PATTERN)


@dataclass(frozen=True, slots=True)
class JobStore:
    """Own the job records folder; every method blocks, so callers run it off the event loop.

    Attributes:
        directory: The private jobs folder.

    """

    directory: Path
    # The lock that the record files share across threads.
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def _read_all(self) -> list[VideoJob]:
        """Read every record, skipping a damaged or oversized file so it never blocks the other jobs."""
        if not self.directory.is_dir():
            return []
        jobs: list[VideoJob] = []
        for path in sorted(self.directory.glob(f'*{JOB_FILES["SUFFIX"]}')):
            try:
                jobs.append(VideoJob.model_validate_json(read_file(path, max_bytes=MAX_FILE_BYTES['JOB'])))
            except (OSError, ValidationError, OpenRouterError):
                continue
        return jobs

    def save(self, job: VideoJob) -> None:
        """Write one record atomically, named by its job ID."""
        path = self.directory / f'{job.job_id}{JOB_FILES["SUFFIX"]}'
        with self._lock:
            save_file(path, (job.model_dump_json(indent=2) + '\n').encode())

    def delete(self, job_id: str) -> None:
        """Delete one record; a record already gone needs no removal."""
        path = self.directory / f'{job_id}{JOB_FILES["SUFFIX"]}'
        with self._lock:
            # reason: Each record name is a job ID that passed validation, inside the private jobs folder.
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


__all__ = ['JOB_ID', 'JobStore']
