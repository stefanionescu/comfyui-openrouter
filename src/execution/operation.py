"""Define the paid request every node hands to the run wrapper, and the upload limit every request shares."""

from __future__ import annotations

import math
from typing import Protocol, TYPE_CHECKING
from ..errors import ErrorCode, ConnectorError
from ..config.messages.media import UPLOAD_LIMIT
from ..config.openrouter import BYTES_PER_MEBIBYTE

if TYPE_CHECKING:
    from collections.abc import Iterable
    from ..state.settings import Settings, ExecutionConfiguration


class Operation[Result](Protocol):
    """One paid OpenRouter request, validated before it is sent."""

    def validate(self, settings: Settings) -> None:
        """Refuse inputs the model or the settings do not allow, before any cost."""
        raise NotImplementedError(settings)

    async def send(self, configuration: ExecutionConfiguration) -> Result:
        """Send the request and return its parsed result."""
        raise NotImplementedError(configuration)


def check_upload_size(media: Iterable[str], settings: Settings) -> None:
    """Refuse encoded media, data URLs or base64 text, larger in total than the maximum upload size."""
    size = sum(len(item) for item in media)
    if size > settings.max_upload_megabytes * BYTES_PER_MEBIBYTE:
        shown = math.ceil(size * 10 / BYTES_PER_MEBIBYTE) / 10
        raise ConnectorError(
            ErrorCode.INVALID_INPUT, UPLOAD_LIMIT.format(size=shown, maximum=settings.max_upload_megabytes)
        )


__all__ = ["Operation", "check_upload_size"]
