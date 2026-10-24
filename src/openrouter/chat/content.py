"""Build a chat completion's messages and body from one chat request."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..options import build_request_body
from ...config.generation.chat import VOICE, EFFORTS

if TYPE_CHECKING:
    from ...state import Json
    from ...state.chat import ChatRequest, ChatSettings
    from ...state.models import Model


def _build_messages(request: ChatRequest) -> list[Json]:
    """List the system prompt, the earlier turns, then the question with its media.

    OpenRouter's image guide recommends the text first, then the images.
    """
    system: list[Json] = [{'role': 'system', 'content': request.system_prompt}] if request.system_prompt.strip() else []
    turns: list[Json] = [{'role': turn.role, 'content': turn.text} for turn in request.conversation.turns]
    images: list[Json] = [{'type': 'image_url', 'image_url': {'url': url}} for url in request.image_urls]
    videos: list[Json] = [{'type': 'video_url', 'video_url': {'url': url}} for url in request.video_urls]
    clips: list[Json] = [
        {'type': 'input_audio', 'input_audio': {'data': clip, 'format': 'wav'}} for clip in request.audio_clips
    ]
    parts: list[Json] = [{'type': 'text', 'text': request.prompt}, *images, *videos, *clips]
    messages = [*system, *turns]
    for document in request.documents:
        if document.file_url is None:
            parts.append({'type': 'text', 'text': f'Document {document.name}:\n\n{document.text}'})
        else:
            parts.append({'type': 'file', 'file': {'filename': document.name, 'file_data': document.file_url}})
    messages.append({'role': 'user', 'content': parts})
    return messages


def _build_output_fields(settings: ChatSettings) -> dict[str, Json]:
    """Ask for images or audio besides text; a music model gets no voice, and OpenRouter streams all audio."""
    fields: dict[str, Json] = {}
    if 'image' in settings.modalities:
        fields['modalities'] = ['image', 'text']
        if settings.aspect_ratio is not None:
            fields['image_config'] = {'aspect_ratio': settings.aspect_ratio}
    if 'audio' in settings.modalities:
        fields['modalities'] = ['text', 'audio']
        fields['stream'] = True
        if settings.voice is not None:
            fields['audio'] = {'voice': settings.voice, 'format': VOICE['FORMAT']}
    return fields


def _choose_effort(effort: str, efforts: tuple[str, ...]) -> str:
    """Choose the effort sent: one the model does not list steps down to the highest below it, or up to its lowest.

    A model that lists no efforts this extension knows gets the effort as chosen.
    """
    known = sorted((level for level in efforts if level in EFFORTS), key=EFFORTS.index)
    if not known or effort in known:
        return effort
    below = [level for level in known if EFFORTS.index(level) < EFFORTS.index(effort)]
    return below[-1] if below else known[0]


def build_body(request: ChatRequest, model: Model) -> dict[str, Json]:
    """Add each control that has a value; the reasoning effort and the seed go only to a model that takes them.

    The reasoning effort steps to one the model lists. With a sampling field, stop text, or a JSON schema, only
    providers that take every field sent may answer.
    """
    settings = request.settings
    parameters = model.parameters
    body: dict[str, Json] = {'model': request.model_id, 'messages': _build_messages(request)}
    if settings.effort is not None and 'reasoning' in parameters:
        body['reasoning'] = {'effort': _choose_effort(settings.effort, model.efforts)}
    if settings.max_tokens > 0:
        field = 'max_tokens' if 'max_completion_tokens' not in parameters else 'max_completion_tokens'
        body[field] = settings.max_tokens
    body.update(settings.sampling)
    if settings.stop:
        body['stop'] = list(settings.stop)
    if 'seed' in parameters:
        body['seed'] = request.seed
    if settings.json_schema is not None:
        body['response_format'] = {'type': 'json_schema', 'json_schema': dict(settings.json_schema)}
    if settings.sampling or settings.stop or settings.json_schema is not None:
        body['provider'] = {'require_parameters': True}
    if settings.pdf_engine is not None and any(document.file_url for document in request.documents):
        body['plugins'] = [{'id': 'file-parser', 'pdf': {'engine': settings.pdf_engine}}]
    return build_request_body(body | _build_output_fields(settings), request.options, 'chat')


__all__ = ['build_body']
