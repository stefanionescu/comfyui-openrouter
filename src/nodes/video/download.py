"""Collect a recorded video job that kept running and billing after a cancel or a restart."""

from __future__ import annotations

import io as memory
from typing import override
import asyncio

from comfy_api.latest import InputImpl, io

from ...state.errors import ErrorCode, OpenRouterError
from ...comfy.runtime import get_runtime
from ...comfy.execution import send_request, wait_for_task
from ...config.namespace import MENUS, NODE_PREFIX
from ...config.messages.videos import JOB_UNKNOWN
from ...openrouter.videos.jobs import JOB_ID
from ...config.generation.videos import JOB_LABEL_SEPARATOR, JOB_TIME_CHARACTERS
from ...openrouter.videos.operation import VideoDownloadOperation


class VideoDownload(io.ComfyNode):
    """Wait for one recorded job and return its video.

    Collecting a job sends only status and download requests, which bill nothing. The same job always
    gives the same video, so ComfyUI's cache is correct and this is not a paid node.
    """

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the recorded jobs when ComfyUI builds the node definitions; the R key reads them again."""
        labels = [
            JOB_LABEL_SEPARATOR.join(
                (job.job_id, job.model_id, job.submitted_at[:JOB_TIME_CHARACTERS].replace('T', ' '))
            )
            for job in get_runtime().jobs.list_jobs()
        ]
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Video: Download',
            category=MENUS['VIDEO'],
            description='Collect a video job that kept running after a cancel or a restart.',
            inputs=[
                io.Combo.Input(
                    'job',
                    options=labels,
                    tooltip='A video job recorded on this server. Press R to list jobs recorded later.',
                )
            ],
            outputs=[io.Video.Output('video', display_name='video')],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    def validate_inputs(cls, **inputs: object) -> bool | str:
        """Take a job recorded after ComfyUI built the node definitions, as long as the label names a job ID.

        ComfyUI skips its own list check only for inputs the validator takes as positional or extra keywords.
        """
        return True if JOB_ID.match(str(inputs.get('job', '')).split(' ', 1)[0]) else JOB_UNKNOWN

    @classmethod
    @override
    async def execute(cls, *, job: str = '') -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls by schema.
        """Read the job's record, wait for it, and download its video."""
        job_id = job.split(' ', 1)[0]
        if JOB_ID.match(job_id) is None:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, JOB_UNKNOWN)
        jobs = get_runtime().jobs
        record = await asyncio.to_thread(jobs.read, job_id)
        # ComfyUI reads the MP4 from memory, so the node writes no temporary file.
        return await wait_for_task(
            send_request(
                VideoDownloadOperation(record, jobs).send,
                lambda content: io.NodeOutput(InputImpl.VideoFromFile(memory.BytesIO(content))),
                cls.hidden.unique_id,
            )
        )


__all__ = ['VideoDownload']
