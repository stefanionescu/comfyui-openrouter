"""Ask any OpenRouter chat model, with the media and outputs the chosen model accepts."""

from __future__ import annotations

import torch
import asyncio
from ..base import PaidNode
from ...tasks import owned_io
from comfy_api.latest import io
from comfy_api.latest import Input
from ...serialization import parse_json
from ...state.capabilities import ChatChoice
from ...errors import ErrorCode, ConnectorError
from typing import cast, ClassVar, TYPE_CHECKING
from comfy_execution.graph import ExecutionBlocker
from ...config.generation.inputs import MODEL_DEFAULT
from ...execution.chat.operation import ChatOperation
from ...config.generation.models import DEFAULT_CHAT_MODEL
from ...config.messages.inputs import ANSWER_SCHEMA_INVALID
from ...comfy.execution import run_request, wait_for_execution
from ...state.chat import Turn, ChatRequest, ChatSettings, Conversation
from ..inputs import read_model, define_model_input, define_request_inputs
from ...config.namespace import CHAT_MENU, NODE_PREFIX, DOCUMENTS_TYPE, CONVERSATION_TYPE
from ...comfy.media import decode_pcm, decode_audio, decode_image, encode_audio, encode_video, encode_images
from ...config.generation.chat import (
    OUTPUTS,
    AUDIO_RATE,
    ALL_EFFORTS,
    PDF_ENGINES,
    DEFAULT_VOICE,
    AUDIO_CHANNELS,
    MAX_TEMPERATURE,
    STEP_TEMPERATURE,
    ALL_ASPECT_RATIOS,
    MAX_AUDIO_SOCKETS,
    MAX_IMAGE_SOCKETS,
    MAX_OUTPUT_TOKENS,
    MAX_VIDEO_SOCKETS,
    DEFAULT_TEMPERATURE,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from ...state.options import RequestOptions
    from ...state.chat import Document, ChatResult


def _define_media(inputs: frozenset[str]) -> list[io.Input]:
    """Offer one growing row of sockets for each kind of media the model reads."""
    media: list[io.Input] = []
    for kind, template, count in (
        ("image", io.Image.Input("image"), MAX_IMAGE_SOCKETS),
        ("video", io.Video.Input("video"), MAX_VIDEO_SOCKETS),
        ("audio", io.Audio.Input("audio"), MAX_AUDIO_SOCKETS),
    ):
        if kind in inputs:
            names = [f"{kind}_{number}" for number in range(1, count + 1)]
            media.append(
                io.Autogrow.Input(
                    "audio" if kind == "audio" else f"{kind}s",
                    template=io.Autogrow.TemplateNames(template, names=names, min=0),
                    tooltip=f"The {kind} for the model to read, one per socket; all go in one request.",
                )
            )
    return media


def _define_outputs(outputs: frozenset[str], aspect_ratios: tuple[str, ...], voice: str) -> list[io.Input]:
    """Offer the outputs choice of a model that makes images or audio, and the image shape or voice it takes."""
    if not outputs:
        return []
    choices = ["text", *(f"{kind} and text" for kind in ("image", "audio") if kind in outputs)]
    controls: list[io.Input] = [
        io.Combo.Input(
            "outputs",
            options=choices,
            default=choices[-1] if len(choices) == 2 else "text",  # noqa: PLR2004 -- reason: A model with one extra output defaults to it.
            tooltip="What the model returns. Choose text for a written answer only.",
        )
    ]
    if "image" in outputs and aspect_ratios:
        controls.append(
            io.Combo.Input(
                "aspect_ratio", display_name="aspect ratio", options=list(aspect_ratios), default=MODEL_DEFAULT
            )
        )
    if "audio" in outputs:
        controls.append(
            io.String.Input(
                "voice", default=voice, tooltip="Voice for spoken replies, such as alloy. Leave blank for music models."
            )
        )
    return controls


def _define_controls(efforts: tuple[str, ...], default_effort: str, max_tokens: int | None) -> list[io.Input]:
    """Offer the reasoning effort and the output token limit a model accepts."""
    controls: list[io.Input] = []
    if efforts:
        controls.append(
            io.Combo.Input(
                "reasoning",
                display_name="reasoning effort",
                options=list(efforts),
                default=default_effort,
                advanced=True,
                tooltip="How much the model thinks before answering.",
            )
        )
    if max_tokens is not None:
        controls.append(
            io.Int.Input(
                "max_output_tokens",
                display_name="max output tokens",
                default=0,
                min=0,
                max=max_tokens,
                advanced=True,
                tooltip="The longest answer in tokens; 0 leaves it to the model.",
            )
        )
    return controls


def _define_sampling(parameters: frozenset[str]) -> list[io.Input]:
    """Offer the temperature and the answer schema, each when the model accepts it."""
    controls: list[io.Input] = []
    if "temperature" in parameters:
        controls.append(
            io.Float.Input(
                "temperature",
                default=DEFAULT_TEMPERATURE,
                min=0,
                max=MAX_TEMPERATURE,
                step=STEP_TEMPERATURE,
                advanced=True,
                tooltip="Higher values vary the answer more.",
            )
        )
    if "structured_outputs" in parameters:
        controls.append(
            io.String.Input(
                "answer_schema",
                display_name="answer schema (JSON)",
                default="",
                multiline=True,
                advanced=True,
                tooltip="A JSON schema the answer must follow; leave empty for free text.",
            )
        )
    return controls


def _define_children(choice: ChatChoice) -> list[io.Input]:
    """Show only the controls, sockets, and outputs this model accepts."""
    effort = choice.default_effort if choice.default_effort in choice.efforts else next(iter(choice.efforts), "")
    has_limit = bool({"max_tokens", "max_completion_tokens"} & choice.parameters)
    limit = (choice.max_output_tokens or MAX_OUTPUT_TOKENS) if has_limit else None
    ratios = (MODEL_DEFAULT, *choice.image_aspect_ratios) if choice.image_aspect_ratios else ()
    return [
        *_define_controls(choice.efforts, effort, limit),
        *_define_sampling(choice.parameters),
        *_define_media(choice.inputs),
        *_define_outputs(choice.outputs, ratios, DEFAULT_VOICE if "audio" in choice.inputs else ""),
    ]


# What a written model ID may use, since the saved list does not describe it.
WRITTEN_MODEL = ChatChoice(
    id="",
    name="",
    inputs=frozenset({"image", "video", "audio", "file"}),
    outputs=frozenset({"image", "audio"}),
    efforts=ALL_EFFORTS,
    default_effort=MODEL_DEFAULT,
    is_reasoning_mandatory=False,
    max_output_tokens=MAX_OUTPUT_TOKENS,
    parameters=frozenset({"max_completion_tokens", "temperature", "structured_outputs", "seed"}),
    image_aspect_ratios=ALL_ASPECT_RATIOS,
)


def _read_settings(model: Mapping[str, object], pdf_engine: str) -> ChatSettings:
    """Read the chosen model's controls; a control the model lacks sends nothing."""
    effort = model.get("reasoning")
    schema_text = str(model.get("answer_schema", "")).strip()
    answer_schema = parse_json(schema_text) if schema_text else None
    if answer_schema is not None and not isinstance(answer_schema, dict):
        raise ConnectorError(ErrorCode.INVALID_INPUT, ANSWER_SCHEMA_INVALID)
    ratio = model.get("aspect_ratio", MODEL_DEFAULT)
    voice = str(model.get("voice", "")).strip()
    temperature = model.get("temperature")
    return ChatSettings(
        effort=str(effort) if effort not in {None, MODEL_DEFAULT} else None,
        max_output_tokens=cast("int", model.get("max_output_tokens", 0)),
        temperature=float(cast("float", temperature)) if temperature is not None else None,
        answer_schema=answer_schema,
        outputs=frozenset(OUTPUTS[str(model.get("outputs", "text"))]),
        aspect_ratio=str(ratio) if ratio != MODEL_DEFAULT else None,
        voice=voice or None,
        pdf_engine=pdf_engine if pdf_engine != MODEL_DEFAULT else None,
    )


def _connected(slots: object) -> list[object]:
    """List the connected sockets of a growing row, in socket order."""
    values = cast("Mapping[str, object]", slots or {})
    ordered = sorted(values.items(), key=lambda item: int(item[0].rsplit("_", 1)[1]))
    return [value for _name, value in ordered if value is not None]


def _encode_media(model: Mapping[str, object]) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Encode every connected image, video, and audio clip; every image of a batch is sent."""
    images = [image for image in _connected(model.get("images")) if isinstance(image, torch.Tensor)]
    videos = [video for video in _connected(model.get("videos")) if isinstance(video, Input.Video)]
    clips = cast("list[Input.Audio]", _connected(model.get("audio")))
    return (
        tuple(url for image in images for url in encode_images(image)),
        tuple(f"data:video/mp4;base64,{encode_video(video)}" for video in videos),
        tuple(encode_audio(clip) for clip in clips),
    )


class ChatAsk(PaidNode):
    """Send one chat completion and return every output the chosen model fills."""

    contract: ClassVar[str] = "chat-ask-v1"

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Build the model dropdown, one option per chat model, with the shared inputs every model uses."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Chat: Ask",
            category=CHAT_MENU,
            description=(
                "Ask any OpenRouter chat model, with images, video, audio, or documents when the model accepts them."
            ),
            inputs=[
                io.String.Input(
                    "prompt", multiline=True, default="", placeholder="prompt", tooltip="The question or instruction."
                ),
                define_model_input("chat", DEFAULT_CHAT_MODEL, _define_children, _define_children(WRITTEN_MODEL)),
                io.String.Input(
                    "system",
                    display_name="system instructions",
                    multiline=True,
                    default="",
                    optional=True,
                    advanced=True,
                    tooltip="Instructions the model follows for the whole answer.",
                ),
                io.Custom(CONVERSATION_TYPE).Input(
                    "conversation", optional=True, tooltip="Connect a previous Chat: Ask to continue its conversation."
                ),
                io.Custom(DOCUMENTS_TYPE).Input(
                    "documents",
                    optional=True,
                    tooltip="Connect Chat: Attach Document. OpenRouter reads PDFs for models without file input.",
                ),
                io.Combo.Input(
                    "pdf_engine",
                    display_name="PDF reader",
                    options=list(PDF_ENGINES),
                    default=MODEL_DEFAULT,
                    advanced=True,
                    tooltip="How OpenRouter reads attached PDFs.",
                ),
                *define_request_inputs(has_seed=True),
            ],
            outputs=[
                io.String.Output("text", display_name="text"),
                io.String.Output("reasoning", display_name="reasoning"),
                io.Image.Output("images", display_name="images", is_output_list=True),
                io.Audio.Output("audio", display_name="audio"),
                io.Custom(CONVERSATION_TYPE).Output("conversation", display_name="conversation"),
            ],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        prompt: str,
        model: dict[str, object],
        seed: int,
        pdf_engine: str = MODEL_DEFAULT,
        system: str = "",
        conversation: Conversation | None = None,
        documents: tuple[Document, ...] | None = None,
        options: RequestOptions | None = None,
    ) -> io.NodeOutput:
        """Encode the connected media inside the owned task, send, and decode what the model made."""
        selection = read_model("chat", model, ChatChoice)
        history = conversation or Conversation(())

        async def start() -> io.NodeOutput:
            """Encode the media inside the owned task, then send the request."""
            images, videos, clips = await owned_io(lambda: _encode_media(model))
            request = ChatRequest(
                model_id=selection.model_id,
                choice=selection.choice,
                system=system,
                prompt=prompt,
                conversation=history,
                image_urls=images,
                video_urls=videos,
                audio_clips=clips,
                documents=documents or (),
                seed=seed,
                settings=_read_settings(model, pdf_engine),
                options=options,
            )
            return await run_request(ChatOperation(request), build_outputs)

        def build_outputs(result: ChatResult) -> io.NodeOutput:
            """Decode the images and audio, and extend the conversation with this exchange."""
            pictures = [decode_image(content)[0] for content in result.images]
            audio: object = ExecutionBlocker(None)
            if result.audio is not None:
                audio = (
                    decode_pcm(result.audio, AUDIO_RATE, AUDIO_CHANNELS)
                    if result.is_pcm
                    else decode_audio(result.audio)
                )
            turns = (*history.turns, Turn("user", prompt), Turn("assistant", result.text))
            return io.NodeOutput(
                result.text,
                result.reasoning,
                pictures or ExecutionBlocker(None),
                audio,
                Conversation(turns),
            )

        return await wait_for_execution(asyncio.create_task(start()))


__all__ = ["ChatAsk"]
