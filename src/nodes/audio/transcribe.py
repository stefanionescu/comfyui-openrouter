"""Turn speech into text, timed segments, and subtitles with any OpenRouter transcription model."""

from __future__ import annotations

import json
import asyncio
from ..base import PaidNode
from dataclasses import asdict
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ...comfy.media import encode_audio
from ..inputs import build_request_inputs
from ...types.audio import TranscriptionRequest
from ...config.namespace import AUDIO_MENU, NODE_PREFIX
from ...config.generation.inputs import MODEL_INPUT, MODEL_TOOLTIP
from ...config.generation.models import DEFAULT_TRANSCRIPTION_MODEL
from ...comfy.execution import wait_for_thread, send_request, wait_for_task
from ...openrouter.transcription import TranscriptionOperation, format_subtitles
from ...config.generation.audio import (
    TIMESTAMP_CHOICES,
    MAX_TRANSCRIPTION_TEMPERATURE,
    TRANSCRIPTION_TEMPERATURE_STEP,
)

if TYPE_CHECKING:
    from comfy_api.latest import Input
    from ...types.options import Options


class AudioTranscribe(PaidNode):
    """Send one audio clip for transcription and return the text, segments, subtitles, and words."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the clip, the model, the language, the timestamps, and the temperature."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Audio: Transcribe",
            category=AUDIO_MENU,
            description=(
                "Turn speech into text, timed segments and words, and subtitles with any OpenRouter "
                "transcription model."
            ),
            inputs=[
                io.Audio.Input("audio", tooltip="One clip. Providers stop after about 60 seconds of processing."),
                io.String.Input(MODEL_INPUT, default=DEFAULT_TRANSCRIPTION_MODEL, tooltip=MODEL_TOOLTIP),
                io.String.Input(
                    "language",
                    default="",
                    tooltip="The spoken language as a two-letter code such as en; leave empty to detect it.",
                ),
                io.Combo.Input(
                    "timestamps",
                    options=list(TIMESTAMP_CHOICES),
                    default=TIMESTAMP_CHOICES[0],
                    tooltip=(
                        "Timed segments for subtitles, and timed words with words and segments. Not every model "
                        "returns them."
                    ),
                ),
                io.Float.Input(
                    "temperature",
                    default=0.0,
                    min=0.0,
                    max=MAX_TRANSCRIPTION_TEMPERATURE,
                    step=TRANSCRIPTION_TEMPERATURE_STEP,
                    advanced=True,
                    tooltip="Higher values vary the transcript more; 0 leaves it to the model.",
                ),
                *build_request_inputs(has_seed=False),
            ],
            outputs=[
                io.String.Output("text", display_name="text"),
                io.String.Output("segments", display_name="segments"),
                io.String.Output("subtitles", display_name="subtitles"),
                io.String.Output("words", display_name="words"),
            ],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        audio: Input.Audio,
        model: str,
        language: str = "",
        timestamps: str = TIMESTAMP_CHOICES[0],
        temperature: float = 0.0,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Encode the clip inside the owned task, then send it."""

        async def send_encoded() -> io.NodeOutput:
            """Encode the clip inside the owned task, then send the request."""
            clip = await wait_for_thread(lambda: encode_audio(audio))
            request = TranscriptionRequest(
                model_id=model.strip(),
                clip=clip,
                language=language.strip().lower(),
                timestamps=timestamps,
                temperature=temperature,
                options=options,
            )
            return await send_request(
                TranscriptionOperation(request),
                lambda result: io.NodeOutput(
                    result.text,
                    json.dumps([asdict(segment) for segment in result.segments], ensure_ascii=False),
                    format_subtitles(result.segments),
                    json.dumps(
                        [{"start": word.start, "end": word.end, "text": word.text} for word in result.words],
                        ensure_ascii=False,
                    ),
                ),
            )

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["AudioTranscribe"]
