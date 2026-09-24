"""Turn speech into text, timed segments, and subtitles with any OpenRouter transcription model."""

from __future__ import annotations

import json
import asyncio
from ..base import PaidNode
from ...tasks import owned_io
from dataclasses import asdict
from comfy_api.latest import io
from ...comfy.media import encode_audio
from typing import ClassVar, TYPE_CHECKING
from ...state.capabilities import TextChoice
from ...state.audio import TranscriptionRequest
from ...config.namespace import AUDIO_MENU, NODE_PREFIX
from ...comfy.execution import run_request, wait_for_execution
from ...config.generation.models import DEFAULT_TRANSCRIPTION_MODEL
from ..inputs import read_model, define_model_input, define_request_inputs
from ...execution.transcription import TranscriptionOperation, format_subtitles
from ...config.generation.audio import TIMESTAMP_CHOICES, MAX_TRANSCRIPTION_TEMPERATURE

if TYPE_CHECKING:
    from comfy_api.latest import Input
    from ...state.options import RequestOptions


class AudioTranscribe(PaidNode):
    """Send one audio clip for transcription and return the text, segments, and subtitles."""

    contract: ClassVar[str] = "audio-transcribe-v1"

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Build the model dropdown, one option per transcription model, and the shared transcription controls."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Audio: Transcribe",
            category=AUDIO_MENU,
            description="Turn speech into text, timed segments, and subtitles with any OpenRouter transcription model.",
            inputs=[
                io.Audio.Input("audio", tooltip="One clip. Providers stop after about 60 seconds of processing."),
                define_model_input("transcription", DEFAULT_TRANSCRIPTION_MODEL, lambda _choice: [], []),
                io.String.Input(
                    "language",
                    display_name="language (two letters)",
                    default="",
                    tooltip="The spoken language, such as en; leave empty to let the model detect it.",
                ),
                io.Combo.Input(
                    "timestamps",
                    options=list(TIMESTAMP_CHOICES),
                    default=TIMESTAMP_CHOICES[0],
                    tooltip="Timed segments for subtitles. Not every model returns them.",
                ),
                io.Float.Input(
                    "temperature",
                    default=0.0,
                    min=0.0,
                    max=MAX_TRANSCRIPTION_TEMPERATURE,
                    step=0.05,
                    advanced=True,
                    tooltip="0 leaves it to the model.",
                ),
                *define_request_inputs(has_seed=False),
            ],
            outputs=[
                io.String.Output("text", display_name="text"),
                io.String.Output("segments", display_name="segments"),
                io.String.Output("subtitles", display_name="subtitles"),
            ],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        audio: Input.Audio,
        model: dict[str, object],
        language: str = "",
        timestamps: str = TIMESTAMP_CHOICES[0],
        temperature: float = 0.0,
        options: RequestOptions | None = None,
    ) -> io.NodeOutput:
        """Encode the clip inside the owned task, then send it."""
        selection = read_model("transcription", model, TextChoice)

        async def start() -> io.NodeOutput:
            """Encode the clip inside the owned task, then send the request."""
            clip = await owned_io(lambda: encode_audio(audio))
            request = TranscriptionRequest(
                model_id=selection.model_id,
                choice=selection.choice,
                clip=clip,
                language=language.strip().lower(),
                timestamps=timestamps,
                temperature=temperature,
                options=options,
            )
            return await run_request(
                TranscriptionOperation(request),
                lambda result: io.NodeOutput(
                    result.text,
                    json.dumps([asdict(segment) for segment in result.segments], ensure_ascii=False),
                    format_subtitles(result.segments),
                ),
            )

        return await wait_for_execution(asyncio.create_task(start()))


__all__ = ["AudioTranscribe"]
