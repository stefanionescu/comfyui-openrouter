"""Turn speech into text, timed segments, and subtitles with any OpenRouter transcription model."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, override
from dataclasses import asdict, dataclass

from comfy_api.latest import Input, io

from ..base import PaidNode, build_request_inputs
from ...comfy.media import encode_audio
from ...state.audio import TranscriptionRequest
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ...config.namespace import MENUS, NODE_PREFIX
from ...config.generation.audio import TIMESTAMP_CHOICES, TRANSCRIPTION_TEMPERATURE
from ...config.generation.inputs import INPUT_NAMES, MODEL_TOOLTIP
from ...config.generation.models import DEFAULT_MODELS
from ...openrouter.transcription import TranscriptionOperation, format_subtitles

if TYPE_CHECKING:
    from ...state.options import Options


@dataclass(frozen=True, slots=True, kw_only=True)
class AudioTranscribeInputs:
    """The saved inputs of Audio: Transcribe, by input name, except the run number."""

    audio: Input.Audio
    model: str
    language: str = ''
    timestamps: str = TIMESTAMP_CHOICES[0]
    temperature: float = 0.0
    options: Options | None = None


class AudioTranscribe(PaidNode):
    """Send one audio clip for transcription and return the text, segments, subtitles, and words."""

    record = AudioTranscribeInputs

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the clip, the model, the language, the timestamps, and the temperature."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Audio: Transcribe',
            category=MENUS['AUDIO'],
            description=(
                'Turn speech into text, timed segments and words, and subtitles with any OpenRouter '
                'transcription model.'
            ),
            inputs=[
                io.Audio.Input('audio', tooltip='One clip. Providers stop after about 60 seconds of processing.'),
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['transcription'], tooltip=MODEL_TOOLTIP),
                io.String.Input(
                    'language',
                    default='',
                    tooltip='The spoken language as a two-letter code such as en; leave empty to detect it.',
                ),
                io.Combo.Input(
                    'timestamps',
                    options=list(TIMESTAMP_CHOICES),
                    default=TIMESTAMP_CHOICES[0],
                    tooltip=(
                        'Timed segments for subtitles, and timed words with words and segments. Not every model '
                        'returns them.'
                    ),
                ),
                io.Float.Input(
                    'temperature',
                    default=0.0,
                    min=0.0,
                    max=TRANSCRIPTION_TEMPERATURE['MAX'],
                    step=TRANSCRIPTION_TEMPERATURE['STEP'],
                    advanced=True,
                    tooltip='Higher values vary the transcript more; 0 leaves it to the model.',
                ),
                *build_request_inputs(has_seed=False),
            ],
            outputs=[
                io.String.Output('text', display_name='text'),
                io.String.Output('segments', display_name='segments'),
                io.String.Output('subtitles', display_name='subtitles'),
                io.String.Output('words', display_name='words'),
            ],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def send(cls, transcription: AudioTranscribeInputs) -> io.NodeOutput:
        """Encode the clip inside the owned task, then send it."""

        async def send_encoded() -> io.NodeOutput:
            """Encode the clip inside the owned task, then send the request."""
            clip = await wait_for_thread(lambda: encode_audio(transcription.audio))
            request = TranscriptionRequest(
                model_id=transcription.model.strip(),
                clip=clip,
                language=transcription.language.strip().lower(),
                timestamps=transcription.timestamps,
                temperature=transcription.temperature,
                options=transcription.options,
            )
            operation = TranscriptionOperation(request)
            return await send_request(
                operation.send,
                lambda result: io.NodeOutput(
                    result.text,
                    json.dumps([asdict(segment) for segment in result.segments], ensure_ascii=False),
                    format_subtitles(result.segments),
                    json.dumps(
                        [{'start': word.start, 'end': word.end, 'text': word.text} for word in result.words],
                        ensure_ascii=False,
                    ),
                ),
                cls.hidden.unique_id,
                validate=operation.validate,
            )

        return await wait_for_task(send_encoded())


__all__ = ['AudioTranscribe']
