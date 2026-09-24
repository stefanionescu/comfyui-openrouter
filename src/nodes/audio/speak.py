"""Turn text into speech with any OpenRouter speech model."""

from __future__ import annotations

import asyncio
from ..base import PaidNode
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ...state.audio import SpeechRequest
from ..inputs import define_request_inputs
from ...openrouter.speech import SpeechOperation
from ...config.namespace import AUDIO_MENU, NODE_PREFIX
from ...config.generation.models import DEFAULT_SPEECH_MODEL
from ...comfy.media import decode_pcm, decode_audio, encode_audio
from ...config.generation.inputs import MODEL_INPUT, MODEL_TOOLTIP
from ...comfy.execution import owned_io, run_request, wait_for_execution
from ...config.generation.audio import (
    MAX_SPEED,
    MIN_SPEED,
    DEFAULT_SPEED,
    SPEECH_FORMATS,
    DEFAULT_SPEECH_VOICE,
    DEFAULT_SPEECH_FORMAT,
)

if TYPE_CHECKING:
    from comfy_api.latest import Input
    from ...state.audio import SpeechResult
    from ...state.options import RequestOptions


def _build_outputs(result: SpeechResult) -> io.NodeOutput:
    """Decode raw PCM with the shape the reply named, or an encoded file such as MP3 by itself."""
    content, pcm = result.audio.content, result.pcm
    audio = decode_pcm(content, pcm.sample_rate, pcm.channels) if pcm else decode_audio(content)
    return io.NodeOutput(audio)


class AudioSpeak(PaidNode):
    """Send one text-to-speech request and return the audio."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the text, the model, the voice, the format, and the voice sample to copy."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Audio: Speak",
            category=AUDIO_MENU,
            description="Turn text into speech with any OpenRouter speech model.",
            inputs=[
                io.String.Input("text", multiline=True, default="", tooltip="What to say."),
                io.String.Input(MODEL_INPUT, default=DEFAULT_SPEECH_MODEL, tooltip=MODEL_TOOLTIP),
                io.String.Input(
                    "voice",
                    default=DEFAULT_SPEECH_VOICE,
                    tooltip="The voice ID, such as Kore for Gemini or alloy for OpenAI. Blank sends none.",
                ),
                io.Combo.Input(
                    "audio_format",
                    display_name="format",
                    options=list(SPEECH_FORMATS),
                    default=DEFAULT_SPEECH_FORMAT,
                    tooltip="The format OpenRouter sends. If the model refuses one, choose the other.",
                ),
                io.Float.Input(
                    "speed",
                    default=DEFAULT_SPEED,
                    min=MIN_SPEED,
                    max=MAX_SPEED,
                    step=0.05,
                    advanced=True,
                    tooltip="Some providers ignore the speed.",
                ),
                io.Audio.Input(
                    "voice_sample",
                    display_name="voice sample",
                    optional=True,
                    tooltip="A short clip of the voice to copy. Only models that clone voices use it.",
                ),
                io.String.Input(
                    "sample_transcript",
                    display_name="sample transcript",
                    default="",
                    advanced=True,
                    tooltip="The words spoken in the voice sample.",
                ),
                *define_request_inputs(has_seed=False),
            ],
            outputs=[io.Audio.Output("audio", display_name="audio")],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        text: str,
        model: str,
        voice: str = DEFAULT_SPEECH_VOICE,
        audio_format: str = DEFAULT_SPEECH_FORMAT,
        speed: float = DEFAULT_SPEED,
        sample_transcript: str = "",
        voice_sample: Input.Audio | None = None,
        options: RequestOptions | None = None,
    ) -> io.NodeOutput:
        """Encode the voice sample inside the owned task, send, and decode the audio."""

        async def start() -> io.NodeOutput:
            """Encode the sample inside the owned task, then send the request."""
            sample = None
            if voice_sample is not None:
                clip = voice_sample
                sample = "data:audio/wav;base64," + await owned_io(lambda: encode_audio(clip))
            request = SpeechRequest(
                model_id=model.strip(),
                text=text,
                voice=voice.strip() or None,
                audio_format=audio_format,
                speed=speed,
                sample=sample,
                sample_transcript=sample_transcript,
                options=options,
            )
            return await run_request(SpeechOperation(request), _build_outputs)

        return await wait_for_execution(asyncio.create_task(start()))


__all__ = ["AudioSpeak"]
