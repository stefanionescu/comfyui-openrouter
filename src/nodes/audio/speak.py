"""Turn text into speech with any OpenRouter speech model."""

from __future__ import annotations

import asyncio
from ..base import PaidNode
from ...tasks import owned_io
from comfy_api.latest import io
from ...state.audio import SpeechRequest
from typing import ClassVar, TYPE_CHECKING
from ...state.capabilities import SpeechChoice
from ...execution.speech import SpeechOperation
from ...config.namespace import AUDIO_MENU, NODE_PREFIX
from ...config.generation.models import DEFAULT_SPEECH_MODEL
from ...comfy.execution import run_request, wait_for_execution
from ...comfy.media import decode_pcm, decode_audio, encode_audio
from ..inputs import read_model, define_model_input, define_request_inputs
from ...config.generation.audio import (
    MAX_SPEED,
    MIN_SPEED,
    DEFAULT_SPEED,
    SPEECH_FORMATS,
    MP3_ONLY_PREFIXES,
    DEFAULT_SPEECH_FORMAT,
)

if TYPE_CHECKING:
    from comfy_api.latest import Input
    from ...state.audio import SpeechResult
    from ...state.options import RequestOptions


def _define_children(choice: SpeechChoice | None) -> list[io.Input]:
    """Offer the model's voices, or a written voice for a written ID, and the format OpenRouter sends.

    The format is PCM by default, and MP3 for models that send nothing else.
    """
    voices: list[io.Input] = []
    if choice is None:
        voices = [
            io.String.Input("voice", default="", tooltip="The voice ID; leave blank for the provider's default voice.")
        ]
    elif choice.voices:
        voices = [io.Combo.Input("voice", options=list(choice.voices), default=choice.voices[0])]
    is_mp3_only = choice is not None and choice.id.startswith(MP3_ONLY_PREFIXES)
    audio_format = io.Combo.Input(
        "audio_format",
        display_name="format",
        options=list(SPEECH_FORMATS),
        default="mp3" if is_mp3_only else DEFAULT_SPEECH_FORMAT,
        tooltip="The format OpenRouter sends. Most models send both. If the model refuses one, choose the other.",
    )
    return [*voices, audio_format]


def _build_outputs(result: SpeechResult) -> io.NodeOutput:
    """Decode raw PCM with the shape the reply named, or an encoded file such as MP3 by itself."""
    content, pcm = result.audio.content, result.pcm
    audio = decode_pcm(content, pcm.sample_rate, pcm.channels) if pcm else decode_audio(content)
    return io.NodeOutput(audio)


class AudioSpeak(PaidNode):
    """Send one text-to-speech request and return the audio."""

    contract: ClassVar[str] = "audio-speak-v1"

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Build the model dropdown, one option per speech model, with a written voice for a written ID."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Audio: Speak",
            category=AUDIO_MENU,
            description="Turn text into speech with any OpenRouter speech model.",
            inputs=[
                io.String.Input("text", multiline=True, default="", tooltip="What to say."),
                define_model_input("speech", DEFAULT_SPEECH_MODEL, _define_children, _define_children(None)),
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
        model: dict[str, object],
        speed: float = DEFAULT_SPEED,
        sample_transcript: str = "",
        voice_sample: Input.Audio | None = None,
        options: RequestOptions | None = None,
    ) -> io.NodeOutput:
        """Encode the voice sample inside the owned task, send, and decode the audio."""
        selection = read_model("speech", model, SpeechChoice)
        voice = str(model.get("voice", "")).strip()
        audio_format = str(model.get("audio_format", DEFAULT_SPEECH_FORMAT))

        async def start() -> io.NodeOutput:
            """Encode the sample inside the owned task, then send the request."""
            sample = None
            if voice_sample is not None:
                clip = voice_sample
                sample = "data:audio/wav;base64," + await owned_io(lambda: encode_audio(clip))
            request = SpeechRequest(
                model_id=selection.model_id,
                choice=selection.choice,
                text=text,
                voice=voice or None,
                audio_format=audio_format,
                speed=speed,
                sample=sample,
                sample_transcript=sample_transcript,
                options=options,
            )
            return await run_request(SpeechOperation(request), _build_outputs)

        return await wait_for_execution(asyncio.create_task(start()))


__all__ = ["AudioSpeak"]
