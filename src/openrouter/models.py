"""Check that a model ID names an OpenRouter model that suits the node, before the request is sent."""

from __future__ import annotations

import re
from .transport import get_model
from typing import TYPE_CHECKING
from pydantic import ValidationError
from ..config.patterns import MODEL_ID_PATTERN
from ..config.messages.run import REPLY_UNREADABLE
from ..types.models import CheckedModel, ModelReply
from ..types.errors import ErrorCode, OpenRouterError
from ..config.openrouter import MODEL_OUTPUTS, ENDPOINT_LABELS
from ..config.messages.models import MODEL_KIND, MODEL_EMPTY, MODEL_UNKNOWN

if TYPE_CHECKING:
    from ..types import Endpoint
    from ..types.settings import ExecutionConfiguration

MODEL_ID = re.compile(MODEL_ID_PATTERN)
# Each model is looked up once per ComfyUI session; an unknown ID is looked up again, since it may be fixed.
_MODELS: dict[str, CheckedModel] = {}


async def check_model(model_id: str, endpoint: Endpoint, configuration: ExecutionConfiguration) -> CheckedModel:
    """Refuse an ID OpenRouter does not list, or a model that makes nothing this endpoint returns."""
    if not model_id:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_EMPTY)
    model = _MODELS.get(model_id)
    if model is None:
        content = await get_model(model_id, configuration) if MODEL_ID.match(model_id) else None
        if content is None:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_UNKNOWN.format(model=model_id))
        try:
            listing = ModelReply.model_validate_json(content).model
        except ValidationError:
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        parameters = (parameter for provider in listing.endpoints for parameter in provider.supported_parameters)
        model = _MODELS[model_id] = CheckedModel(
            frozenset(listing.architecture.output_modalities), frozenset(parameters)
        )
    if model.outputs.isdisjoint(MODEL_OUTPUTS[endpoint]):
        kind = ENDPOINT_LABELS[endpoint]
        raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_KIND.format(model=model_id, kind=kind))
    return model


__all__ = ["check_model"]
