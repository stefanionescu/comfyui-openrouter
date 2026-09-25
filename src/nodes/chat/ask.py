"""Ask any OpenRouter chat model, with images, video, audio, or documents, for text, images, or audio."""

from __future__ import annotations

import asyncio
from ..base import PaidNode
from comfy_api.latest import io
from typing import cast, TYPE_CHECKING
from ...types.parsing import parse_json
from comfy_execution.graph import ExecutionBlocker
from ...openrouter.chat.operation import ChatOperation
from ...types.errors import ErrorCode, OpenRouterError
from ..inputs import encode_media, build_request_inputs
from ...config.generation.models import DEFAULT_CHAT_MODEL
from ...config.messages.inputs import ANSWER_SCHEMA_INVALID
from ...comfy.media import decode_pcm, decode_audio, decode_image
from ...types.chat import Turn, ChatRequest, ChatSettings, Conversation
from ...comfy.execution import wait_for_thread, send_request, wait_for_task
from ...config.generation.inputs import MODEL_INPUT, MODEL_DEFAULT, MODEL_TOOLTIP
from ...config.namespace import CHAT_MENU, NODE_PREFIX, DOCUMENTS_TYPE, CONVERSATION_TYPE
from ...config.generation.chat import (
    EFFORTS,
    OUTPUTS,
    AUDIO_RATE,
    PDF_ENGINES,
    ASPECT_RATIOS,
    DEFAULT_VOICE,
    AUDIO_CHANNELS,
    MAX_TEMPERATURE,
    SET_TEMPERATURE,
    TEMPERATURE_STEP,
    TEMPERATURE_INPUT,
    DEFAULT_TEMPERATURE,
    TEMPERATURE_VALUE_INPUT,
)

if TYPE_CHECKING:
    import torch
    from ...types import Json
    from comfy_api.latest import Input
    from collections.abc import Mapping
    from ...types.options import Options
    from ...types.chat import Document, ChatResult


# One socket for each kind of media; everything connected goes in one request, each item at its own size.
MEDIA = (
    io.Image.Input(
        "images",
        optional=True,
        tooltip="Images for the model to read: one, a batch, or a list. Create List joins several Load Image nodes.",
    ),
    io.Video.Input("videos", optional=True, tooltip="Videos for the model to read. Create List joins several."),
    io.Audio.Input("audio", optional=True, tooltip="Audio clips for the model to read. Create List joins several."),
)


# The controls a chat model may take, what it makes besides text, and how it reads PDFs; each left at its default
# sends nothing.
CONTROLS = (
    io.Combo.Input(
        "reasoning_effort",
        display_name="reasoning effort",
        options=list(EFFORTS),
        default=MODEL_DEFAULT,
        advanced=True,
        tooltip="How much the model thinks before answering.",
    ),
    io.Int.Input(
        "max_tokens",
        display_name="max tokens",
        default=0,
        min=0,
        advanced=True,
        tooltip="The longest answer in tokens; 0 leaves it to the model.",
    ),
    io.DynamicCombo.Input(
        TEMPERATURE_INPUT,
        options=[
            io.DynamicCombo.Option(MODEL_DEFAULT, []),
            io.DynamicCombo.Option(
                SET_TEMPERATURE,
                [
                    io.Float.Input(
                        TEMPERATURE_VALUE_INPUT,
                        display_name="value",
                        default=DEFAULT_TEMPERATURE,
                        min=0,
                        max=MAX_TEMPERATURE,
                        step=TEMPERATURE_STEP,
                        advanced=True,
                        tooltip="Higher values vary the answer more.",
                    )
                ],
            ),
        ],
        tooltip="How much the answer varies. Set sends a value to models that take a temperature.",
        extra_dict={"advanced": True},
    ),
    io.Combo.Input(
        "outputs",
        options=list(OUTPUTS),
        default="text",
        tooltip="What the model returns. Images and audio need a model that makes them.",
    ),
    io.Combo.Input(
        "aspect_ratio",
        display_name="aspect ratio",
        options=[MODEL_DEFAULT, *ASPECT_RATIOS],
        default=MODEL_DEFAULT,
        tooltip="The shape of the images the model makes.",
    ),
    io.String.Input(
        "voice",
        default=DEFAULT_VOICE,
        tooltip="Voice for spoken replies, such as alloy. Leave blank for music models.",
    ),
    io.Combo.Input(
        "pdf_engine",
        display_name="PDF engine",
        options=list(PDF_ENGINES),
        default=MODEL_DEFAULT,
        advanced=True,
        tooltip="How OpenRouter reads attached PDFs.",
    ),
)


def _read_temperature(choice: Mapping[str, object] | None) -> float | None:
    """Read the set temperature; model default, or no choice from a node that calls this one, sends none."""
    if choice is None or choice[TEMPERATURE_INPUT] != SET_TEMPERATURE:
        return None
    return float(cast("float", choice[TEMPERATURE_VALUE_INPUT]))


def _read_schema(text: str) -> Mapping[str, Json] | None:
    """Read the answer schema, which must be a JSON object; empty text means free text."""
    if not text.strip():
        return None
    schema = parse_json(text)
    if not isinstance(schema, dict):
        raise OpenRouterError(ErrorCode.INVALID_INPUT, ANSWER_SCHEMA_INVALID)
    return schema


def _build_outputs(result: ChatResult, history: Conversation, prompt: str) -> io.NodeOutput:
    """Decode the images and audio, and extend the conversation with this exchange."""
    pictures = [decode_image(content)[0] for content in result.images]
    sound: object = ExecutionBlocker(None)
    if result.audio is not None:
        sound = decode_pcm(result.audio, AUDIO_RATE, AUDIO_CHANNELS) if result.is_pcm else decode_audio(result.audio)
    turns = (*history.turns, Turn("user", prompt), Turn("assistant", result.text))
    return io.NodeOutput(result.text, result.reasoning, pictures or ExecutionBlocker(None), sound, Conversation(turns))


class ChatAsk(PaidNode):
    """Send one chat completion and return every output the model fills."""

    list_inputs = frozenset({"images", "videos", "audio"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the prompt, the model, the media sockets, and every control a chat model may take."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Chat: Ask",
            category=CHAT_MENU,
            description=(
                "Ask any OpenRouter chat model, with images, video, audio, or documents when the model accepts them."
            ),
            inputs=[
                io.String.Input(MODEL_INPUT, default=DEFAULT_CHAT_MODEL, tooltip=MODEL_TOOLTIP),
                io.Custom(CONVERSATION_TYPE).Input(
                    "conversation", optional=True, tooltip="Connect a previous Chat: Ask to continue its conversation."
                ),
                io.Custom(DOCUMENTS_TYPE).Input(
                    "documents",
                    optional=True,
                    tooltip="Connect Chat: Attach Document. OpenRouter converts PDFs for models that read only text.",
                ),
                *MEDIA,
                *CONTROLS,
                *build_request_inputs(has_seed=True),
                io.String.Input(
                    "answer_schema",
                    display_name="answer schema",
                    placeholder="answer schema",
                    default="",
                    multiline=True,
                    advanced=True,
                    tooltip="A JSON schema the answer must follow; leave empty for free text.",
                ),
                io.String.Input(
                    "prompt", multiline=True, default="", placeholder="prompt", tooltip="The question or instruction."
                ),
                io.String.Input(
                    "system_prompt",
                    display_name="system prompt",
                    placeholder="system prompt",
                    multiline=True,
                    default="",
                    optional=True,
                    advanced=True,
                    tooltip="Instructions the model follows for the whole answer.",
                ),
            ],
            outputs=[
                io.String.Output("text", display_name="text"),
                io.String.Output("reasoning", display_name="reasoning"),
                io.Image.Output("images", display_name="images", is_output_list=True),
                io.Audio.Output("audio", display_name="audio"),
                io.Custom(CONVERSATION_TYPE).Output("conversation", display_name="conversation"),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        prompt: str,
        model: str,
        seed: int,
        reasoning_effort: str = MODEL_DEFAULT,
        max_tokens: int = 0,
        temperature: Mapping[str, object] | None = None,
        answer_schema: str = "",
        outputs: str = "text",
        aspect_ratio: str = MODEL_DEFAULT,
        voice: str = DEFAULT_VOICE,
        pdf_engine: str = MODEL_DEFAULT,
        system_prompt: str = "",
        conversation: Conversation | None = None,
        documents: tuple[Document, ...] | None = None,
        images: list[torch.Tensor] | None = None,
        videos: list[Input.Video] | None = None,
        audio: list[Input.Audio] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Encode the connected media inside the owned task, send, and decode what the model made."""
        history = conversation or Conversation(())
        settings = ChatSettings(
            effort=reasoning_effort if reasoning_effort != MODEL_DEFAULT else None,
            max_tokens=max_tokens,
            temperature=_read_temperature(temperature),
            answer_schema=_read_schema(answer_schema),
            outputs=frozenset(OUTPUTS[outputs]),
            aspect_ratio=aspect_ratio if aspect_ratio != MODEL_DEFAULT else None,
            voice=voice.strip() or None,
            pdf_engine=pdf_engine if pdf_engine != MODEL_DEFAULT else None,
        )

        async def send_encoded() -> io.NodeOutput:
            """Encode the media inside the owned task, then send the request."""
            image_urls, video_urls, clips = await wait_for_thread(lambda: encode_media(images, videos, audio))
            request = ChatRequest(
                model_id=model.strip(),
                system_prompt=system_prompt,
                prompt=prompt,
                conversation=history,
                image_urls=image_urls,
                video_urls=video_urls,
                audio_clips=clips,
                documents=documents or (),
                seed=seed,
                settings=settings,
                options=options,
            )
            return await send_request(
                ChatOperation(request), lambda result: _build_outputs(result, history, prompt), cls.hidden.unique_id
            )

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["ChatAsk"]
