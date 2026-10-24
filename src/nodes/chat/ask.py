"""Ask any OpenRouter chat model, with images, video, audio, or documents, for text, images, or audio."""

from __future__ import annotations

from typing import TYPE_CHECKING, override
from dataclasses import replace, dataclass

from comfy_api.latest import Input, io
from comfy_execution.graph import ExecutionBlocker

from ..base import PaidNode, build_request_inputs
from ..inputs import encode_media
from ...state.chat import Turn, ChatRequest, ChatSettings, Conversation
from ...comfy.media import decode_pcm, decode_audio, decode_image
from ...state.errors import ErrorCode, OpenRouterError
from ...state.parsing import parse_json
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ...config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ...config.generation.chat import (
    VOICE,
    EFFORTS,
    OUTPUTS,
    SAMPLING,
    PDF_ENGINES,
    VOICE_AUDIO,
    SAMPLING_DECIMALS,
    SAMPLING_TOOLTIPS,
    IMAGE_ASPECT_RATIOS,
    SAMPLING_WHOLE_NUMBERS,
)
from ...config.messages.inputs import JSON_SCHEMA_INVALID
from ...config.generation.inputs import INPUT_NAMES, VALUE_CHOICE, MODEL_DEFAULT, MODEL_TOOLTIP
from ...config.generation.models import DEFAULT_MODELS
from ...openrouter.chat.operation import ChatOperation

if TYPE_CHECKING:
    from collections.abc import Mapping

    import torch

    from ...state import Json
    from ...state.chat import Document, ChatResult
    from ...state.options import Options


# The connected images, videos, and audio clips, as their sockets hold them.
type _Media = tuple[list[torch.Tensor] | None, list[Input.Video] | None, list[Input.Audio] | None]


# One socket for each kind of media; everything connected goes in one request, each item at its own size.
MEDIA = (
    io.Image.Input(
        'images',
        optional=True,
        tooltip='Images for the model to read: one, a batch, or a list. Create List joins several Load Image nodes.',
    ),
    io.Video.Input('videos', optional=True, tooltip='Videos for the model to read. Create List joins several.'),
    io.Audio.Input('audio', optional=True, tooltip='Audio clips for the model to read. Create List joins several.'),
)


def _build_sampling(name: str) -> io.DynamicCombo.Input:
    """Build one sampling dropdown: default sends nothing, and custom shows the value at OpenRouter's own range."""
    tooltip = SAMPLING_TOOLTIPS[name]
    value: io.Input
    if name in SAMPLING_WHOLE_NUMBERS:
        start, minimum = SAMPLING_WHOLE_NUMBERS[name]
        value = io.Int.Input(VALUE_CHOICE['VALUE'], default=start, min=minimum, advanced=True, tooltip=tooltip)
    else:
        start, minimum, maximum, step = SAMPLING_DECIMALS[name]
        value = io.Float.Input(
            VALUE_CHOICE['VALUE'], default=start, min=minimum, max=maximum, step=step, advanced=True, tooltip=tooltip
        )
    options = [io.DynamicCombo.Option(MODEL_DEFAULT, []), io.DynamicCombo.Option(VALUE_CHOICE['SET'], [value])]
    return io.DynamicCombo.Input(
        name, options=options, tooltip=f'{tooltip} Choose custom to send a value.', extra_dict={'advanced': True}
    )


# The controls a chat model may take, what it makes besides text, and how it reads PDFs; each left at its default
# sends nothing.
CONTROLS = (
    io.Combo.Input(
        'reasoning_effort',
        options=list(EFFORTS),
        default=MODEL_DEFAULT,
        advanced=True,
        tooltip='How much the model thinks before answering.',
    ),
    io.Int.Input(
        'max_tokens',
        default=0,
        min=0,
        advanced=True,
        tooltip='The longest answer in tokens; 0 leaves it to the model.',
    ),
    *(_build_sampling(name) for name in SAMPLING),
    io.Combo.Input(
        'outputs',
        options=list(OUTPUTS),
        default='text',
        tooltip='What the model returns. Images and audio need a model that makes them.',
    ),
    io.Combo.Input(
        'aspect_ratio',
        options=list(IMAGE_ASPECT_RATIOS),
        default=MODEL_DEFAULT,
        tooltip='The shape of the images the model makes.',
    ),
    io.String.Input(
        'voice',
        default=VOICE['DEFAULT'],
        tooltip='Voice for spoken replies, such as alloy. Leave blank for music models.',
    ),
    io.Combo.Input(
        'pdf_engine',
        options=list(PDF_ENGINES),
        default=MODEL_DEFAULT,
        advanced=True,
        tooltip='How OpenRouter reads attached PDFs.',
    ),
)


def _read_schema(text: str) -> Mapping[str, Json] | None:
    """Read the response_format.json_schema object, which must be a JSON object; empty text means free text."""
    if not text.strip():
        return None
    schema = parse_json(text)
    if not isinstance(schema, dict):
        raise OpenRouterError(ErrorCode.INVALID_INPUT, JSON_SCHEMA_INVALID)
    return schema


def _build_outputs(result: ChatResult, history: Conversation, prompt: str) -> io.NodeOutput:
    """Decode the images and audio, and extend the conversation with this exchange."""
    pictures = [decode_image(content)[0] for content in result.images]
    sound: object = ExecutionBlocker(None)
    if result.audio is not None:
        sound = (
            decode_pcm(result.audio, VOICE_AUDIO['SAMPLE_RATE'], VOICE_AUDIO['CHANNELS'])
            if result.is_pcm
            else decode_audio(result.audio)
        )
    turns = (*history.turns, Turn('user', prompt), Turn('assistant', result.text))
    reasoning: object = result.reasoning or ExecutionBlocker(None)
    return io.NodeOutput(result.text, reasoning, pictures or ExecutionBlocker(None), sound, Conversation(turns))


async def _send_media(request: ChatRequest, media: _Media, node_id: str) -> io.NodeOutput:
    """Encode the connected media inside the owned task, then send the request and decode what the model made."""
    image_urls, video_urls, clips = await wait_for_thread(lambda: encode_media(*media))
    encoded = replace(request, image_urls=image_urls, video_urls=video_urls, audio_clips=clips)
    operation = ChatOperation(encoded)
    return await send_request(
        operation.send,
        lambda result: _build_outputs(result, request.conversation, request.prompt),
        node_id,
        validate=operation.validate,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class ChatAskInputs:
    """The saved inputs of Chat: Ask, by input name, except the run number."""

    prompt: str
    model: str
    seed: int
    reasoning_effort: str = MODEL_DEFAULT
    max_tokens: int = 0
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    min_p: float | None = None
    top_a: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    repetition_penalty: float | None = None
    json_schema: str = ''
    stop: str = ''
    outputs: str = 'text'
    aspect_ratio: str = MODEL_DEFAULT
    voice: str = VOICE['DEFAULT']
    pdf_engine: str = MODEL_DEFAULT
    system_prompt: str = ''
    conversation: Conversation | None = None
    documents: tuple[Document, ...] | None = None
    images: list[torch.Tensor] | None = None
    videos: list[Input.Video] | None = None
    audio: list[Input.Audio] | None = None
    options: Options | None = None


class ChatAsk(PaidNode):
    """Send one chat completion and return every output the model fills."""

    record = ChatAskInputs

    list_inputs = frozenset({'images', 'videos', 'audio'})
    choice_inputs = frozenset(SAMPLING)

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the prompt, the model, the media sockets, and every control a chat model may take."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Chat: Ask',
            category=MENUS['CHAT'],
            description=(
                'Ask any OpenRouter chat model, with images, video, audio, or documents when the model accepts them.'
            ),
            inputs=[
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['chat'], tooltip=MODEL_TOOLTIP),
                io.Custom(SOCKET_TYPES['CONVERSATION']).Input(
                    'conversation', optional=True, tooltip='Connect a previous Chat: Ask to continue its conversation.'
                ),
                io.Custom(SOCKET_TYPES['DOCUMENTS']).Input(
                    'documents',
                    optional=True,
                    tooltip='Connect Chat: Attach Document. OpenRouter converts PDFs for models that read only text.',
                ),
                *MEDIA,
                *CONTROLS,
                *build_request_inputs(has_seed=True),
                io.String.Input(
                    'json_schema',
                    default='',
                    multiline=True,
                    advanced=True,
                    tooltip=(
                        'Sent as response_format.json_schema: a JSON object with a name and a schema. Leave it empty '
                        'for free text.'
                    ),
                ),
                io.String.Input(
                    'stop',
                    default='',
                    multiline=True,
                    advanced=True,
                    tooltip='Text that ends the answer, one per line. Leave it empty to send none.',
                ),
                io.String.Input('prompt', multiline=True, default='', tooltip='The question or instruction.'),
                io.String.Input(
                    'system_prompt',
                    multiline=True,
                    default='',
                    optional=True,
                    advanced=True,
                    tooltip='Instructions the model follows for the whole answer.',
                ),
            ],
            outputs=[
                io.String.Output('text', display_name='text'),
                io.String.Output('reasoning', display_name='reasoning'),
                io.Image.Output('images', display_name='images', is_output_list=True),
                io.Audio.Output('audio', display_name='audio'),
                io.Custom(SOCKET_TYPES['CONVERSATION']).Output('conversation', display_name='conversation'),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def send(cls, chat: ChatAskInputs) -> io.NodeOutput:
        """Build the request, then encode the connected media inside the owned task, send, and decode the answer."""
        choices = (
            chat.temperature,
            chat.top_p,
            chat.top_k,
            chat.min_p,
            chat.top_a,
            chat.frequency_penalty,
            chat.presence_penalty,
            chat.repetition_penalty,
        )
        request = ChatRequest(
            model_id=chat.model.strip(),
            system_prompt=chat.system_prompt,
            prompt=chat.prompt,
            conversation=chat.conversation or Conversation(()),
            image_urls=(),
            video_urls=(),
            audio_clips=(),
            documents=chat.documents or (),
            seed=chat.seed,
            settings=ChatSettings(
                effort=chat.reasoning_effort if chat.reasoning_effort != MODEL_DEFAULT else None,
                max_tokens=chat.max_tokens,
                sampling={name: value for name, value in zip(SAMPLING, choices, strict=True) if value is not None},
                stop=tuple(line for line in chat.stop.splitlines() if line),
                json_schema=_read_schema(chat.json_schema),
                outputs=frozenset(OUTPUTS[chat.outputs]),
                aspect_ratio=chat.aspect_ratio if chat.aspect_ratio != MODEL_DEFAULT else None,
                voice=chat.voice.strip() or None,
                pdf_engine=chat.pdf_engine if chat.pdf_engine != MODEL_DEFAULT else None,
            ),
            options=chat.options,
        )
        media = _send_media(request, (chat.images, chat.videos, chat.audio), cls.hidden.unique_id)
        return await wait_for_task(media)


__all__ = ['ChatAsk']
