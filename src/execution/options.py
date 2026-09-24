"""Merge the routing and extra fields of a Request Options node into one endpoint's request body."""

from __future__ import annotations

from typing import TYPE_CHECKING
from ..errors import ErrorCode, ConnectorError
from ..config.messages.inputs import OPTION_UNSUPPORTED, OPTION_RESERVED_FIELD
from ..config.openrouter import ENDPOINT_LABELS, ROUTING_FIELDS, RESERVED_FIELDS

if TYPE_CHECKING:
    from ..state import Json
    from collections.abc import Mapping
    from ..state.capabilities import Endpoint
    from ..state.options import RequestOptions


def apply_options(body: Mapping[str, Json], options: RequestOptions | None, endpoint: Endpoint) -> dict[str, Json]:
    """Add the options this endpoint accepts, refusing any it does not before a request is sent."""
    merged = dict(body)
    if options is None:
        return merged
    routing: dict[str, Json] = {
        "order": list(options.order) or None,
        "only": list(options.only) or None,
        "ignore": list(options.ignore) or None,
        "sort": options.sort,
        "allow_fallbacks": options.allow_fallbacks,
        "data_collection": options.data_collection,
        "zdr": options.zdr,
        "max_price": dict(options.max_price) or None,
        "options": dict(options.provider_options) or None,
    }
    provider: dict[str, Json] = {field: value for field, value in routing.items() if value is not None}
    for field in provider:
        if field not in ROUTING_FIELDS[endpoint]:
            label = ENDPOINT_LABELS[endpoint]
            raise ConnectorError(ErrorCode.INVALID_INPUT, OPTION_UNSUPPORTED.format(endpoint=label, field=field))
    for field in options.extra_fields:
        if field in RESERVED_FIELDS[endpoint]:
            raise ConnectorError(ErrorCode.INVALID_INPUT, OPTION_RESERVED_FIELD.format(field=field))
    merged.update(options.extra_fields)
    if provider:
        merged["provider"] = provider
    return merged


__all__ = ["apply_options"]
