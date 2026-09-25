"""Build a chat completion's messages and body from one chat request."""

from __future__ import annotations

from typing import TYPE_CHECKING
from ..options import build_request_body
from ...config.generation.chat import AUDIO_FORMAT, ANSWER_SCHEMA_NAME

if TYPE_CHECKING:
    from ...types import Json
    from ...types.chat import ChatRequest, ChatSettings


def _build_messages(request: ChatRequest) -> list[Json]:
    """List the system prompt, the earlier turns, then the question with its media.

    OpenRouter's image guide recommends the text first, then the images.
    """
    system: list[Json] = [{"role": "system", "content": request.system_prompt}] if request.system_prompt.strip() else []
    turns: list[Json] = [{"role": turn.role, "content": turn.text} for turn in request.conversation.turns]
    images: list[Json] = [{"type": "image_url", "image_url": {"url": url}} for url in request.image_urls]
    videos: list[Json] = [{"type": "video_url", "video_url": {"url": url}} for url in request.video_urls]
    clips: list[Json] = [
        {"type": "input_audio", "input_audio": {"data": clip, "format": "wav"}} for clip in request.audio_clips
    ]
    parts: list[Json] = [{"type": "text", "text": request.prompt}, *images, *videos, *clips]
    messages = [*system, *turns]
    for document in request.documents:
        if document.file_url is None:
            parts.append({"type": "text", "text": f"Document {document.name}:\n\n{document.text}"})
        else:
            parts.append({"type": "file", "file": {"filename": document.name, "file_data": document.file_url}})
    messages.append({"role": "user", "content": parts})
    return messages


def _build_output_fields(settings: ChatSettings) -> dict[str, Json]:
    """Ask for images or audio besides text; a music model gets no voice, and OpenRouter streams all audio."""
    fields: dict[str, Json] = {}
    if "image" in settings.outputs:
        fields["modalities"] = ["image", "text"]
        if settings.aspect_ratio is not None:
            fields["image_config"] = {"aspect_ratio": settings.aspect_ratio}
    if "audio" in settings.outputs:
        fields["modalities"] = ["text", "audio"]
        fields["stream"] = True
        if settings.voice is not None:
            fields["audio"] = {"voice": settings.voice, "format": AUDIO_FORMAT}
    return fields


def build_body(request: ChatRequest, parameters: frozenset[str]) -> dict[str, Json]:
    """Add each control that is set; the reasoning effort, temperature, and seed go only to a model that takes them.

    With an answer schema, only providers that follow it may answer.
    """
    settings = request.settings
    body: dict[str, Json] = {"model": request.model_id, "messages": _build_messages(request)}
    if settings.effort is not None and "reasoning" in parameters:
        body["reasoning"] = {"effort": settings.effort}
    if settings.max_tokens > 0:
        field = "max_tokens" if "max_completion_tokens" not in parameters else "max_completion_tokens"
        body[field] = settings.max_tokens
    if settings.temperature is not None and "temperature" in parameters:
        body["temperature"] = settings.temperature
    if "seed" in parameters:
        body["seed"] = request.seed
    if settings.answer_schema is not None:
        schema: dict[str, Json] = {"name": ANSWER_SCHEMA_NAME, "schema": dict(settings.answer_schema), "strict": True}
        body["response_format"] = {"type": "json_schema", "json_schema": schema}
        body["provider"] = {"require_parameters": True}
    if settings.pdf_engine is not None and any(document.file_url for document in request.documents):
        body["plugins"] = [{"id": "file-parser", "pdf": {"engine": settings.pdf_engine}}]
    return build_request_body(body | _build_output_fields(settings), request.options, "chat")


__all__ = ["build_body"]
