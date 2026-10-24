"""Turn text into speech with any OpenRouter speech model."""

from __future__ import annotations

from typing import TYPE_CHECKING, override
from dataclasses import dataclass

from comfy_api.latest import Input, io

from ..base import PaidNode, build_request_inputs
from ...comfy.media import decode_pcm, decode_audio, encode_audio
from ...state.audio import SpeechRequest
from ...config.media import WAV
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ...config.namespace import MENUS, NODE_PREFIX
from ...openrouter.speech import SpeechOperation
from ...config.generation.audio import SPEED, SPEECH_FORMATS, SPEECH_DEFAULTS
from ...config.generation.inputs import INPUT_NAMES, MODEL_TOOLTIP
from ...config.generation.models import DEFAULT_MODELS

if TYPE_CHECKING:
    from ...state.audio import SpeechResult
    from ...state.options import Options


def _build_outputs(result: SpeechResult) -> io.NodeOutput:
    """Decode raw PCM with the shape the reply named, or an encoded file such as MP3 by itself."""
    content, pcm = result.audio.content, result.pcm
    audio = decode_pcm(content, pcm.sample_rate, pcm.channels) if pcm else decode_audio(content)
    return io.NodeOutput(audio)


@dataclass(frozen=True, slots=True, kw_only=True)
class AudioSpeakInputs:
    """The saved inputs of Audio: Speak, by input name, except the run number."""

    text: str
    model: str
    voice: str = SPEECH_DEFAULTS['VOICE']
    audio_format: str = SPEECH_DEFAULTS['FORMAT']
    speed: float = SPEED['DEFAULT']
    sample_transcript: str = ''
    voice_sample: Input.Audio | None = None
    options: Options | None = None


class AudioSpeak(PaidNode):
    """Send one text-to-speech request and return the audio."""

    record = AudioSpeakInputs

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the text, the model, the voice, the format, and the voice sample to copy."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Audio: Speak',
            category=MENUS['AUDIO'],
            description='Turn text into speech with any OpenRouter speech model.',
            inputs=[
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['speech'], tooltip=MODEL_TOOLTIP),
                io.String.Input(
                    'voice',
                    default=SPEECH_DEFAULTS['VOICE'],
                    tooltip='The voice ID, such as Kore for Gemini or alloy for OpenAI. Blank sends none.',
                ),
                io.Combo.Input(
                    'audio_format',
                    options=list(SPEECH_FORMATS),
                    default=SPEECH_DEFAULTS['FORMAT'],
                    tooltip='The audio file format OpenRouter sends back. If the model refuses one, choose the other.',
                ),
                io.Float.Input(
                    'speed',
                    default=SPEED['DEFAULT'],
                    min=SPEED['MIN'],
                    max=SPEED['MAX'],
                    step=SPEED['STEP'],
                    advanced=True,
                    tooltip='How fast the voice speaks, 1 being normal. Some providers ignore it.',
                ),
                io.Audio.Input(
                    'voice_sample',
                    optional=True,
                    tooltip='A short clip of the voice to copy. Only models that clone voices use it.',
                ),
                io.String.Input(
                    'sample_transcript',
                    default='',
                    advanced=True,
                    tooltip='The words spoken in voice_sample.',
                ),
                *build_request_inputs(has_seed=False),
                io.String.Input('text', multiline=True, default='', tooltip='What to say.'),
            ],
            outputs=[io.Audio.Output('audio', display_name='audio')],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def send(cls, speech: AudioSpeakInputs) -> io.NodeOutput:
        """Encode the voice sample inside the owned task, send, and decode the audio."""

        async def send_encoded() -> io.NodeOutput:
            """Encode the sample inside the owned task, then send the request."""
            sample = None
            if speech.voice_sample is not None:
                clip = speech.voice_sample
                sample = WAV['URL_PREFIX'] + await wait_for_thread(lambda: encode_audio(clip))
            request = SpeechRequest(
                model_id=speech.model.strip(),
                text=speech.text,
                voice=speech.voice.strip() or None,
                audio_format=speech.audio_format,
                speed=speech.speed,
                sample=sample,
                sample_transcript=speech.sample_transcript,
                options=speech.options,
            )
            operation = SpeechOperation(request)
            return await send_request(operation.send, _build_outputs, cls.hidden.unique_id, validate=operation.validate)

        return await wait_for_task(send_encoded())


__all__ = ['AudioSpeak']
