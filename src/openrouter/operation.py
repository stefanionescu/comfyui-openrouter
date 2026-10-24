"""Check the upload limit that every paid request shares."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ..config.units import BYTES_PER_MEBIBYTE
from ..state.errors import ErrorCode, OpenRouterError
from ..config.messages.media import UPLOAD_LIMIT

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ..state.settings import Settings


def validate_upload_size(media: Iterable[str], settings: Settings) -> None:
    """Refuse encoded media, data URLs or base64 text, larger in total than the maximum upload size."""
    size = sum(len(item) for item in media)
    if size > settings.max_upload_megabytes * BYTES_PER_MEBIBYTE:
        shown = math.ceil(size * 10 / BYTES_PER_MEBIBYTE) / 10
        raise OpenRouterError(
            ErrorCode.INVALID_INPUT, UPLOAD_LIMIT.format(size=shown, maximum=settings.max_upload_megabytes)
        )


__all__ = ['validate_upload_size']
