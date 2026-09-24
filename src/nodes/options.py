"""Choose providers, price caps, and extra request fields once, for any number of OpenRouter nodes."""

from __future__ import annotations

import re
from decimal import Decimal
from comfy_api.latest import io
from types import MappingProxyType
from ..types.parsing import parse_json
from typing import override, TYPE_CHECKING
from ..config.patterns import PROVIDER_SLUG_PATTERN
from ..config.generation.inputs import MODEL_DEFAULT
from ..types.errors import ErrorCode, OpenRouterError
from ..types.options import RequestOptions as OptionsRecord
from ..config.namespace import NODE_PREFIX, SHARED_MENU, OPTIONS_TYPE
from ..config.messages.inputs import OPTIONS_JSON, OPTIONS_SIZE, PROVIDER_SLUG
from ..config.openrouter import SORT_CHOICES, MAX_PROVIDERS, YES_NO_CHOICES, MAX_OPTION_BYTES, COLLECTION_CHOICES

if TYPE_CHECKING:
    from ..types import Json

PROVIDER = re.compile(PROVIDER_SLUG_PATTERN)
# The routing dropdowns: input, label, choices, and tooltip.
ROUTING_CHOICES = (
    ("sort", "sort", SORT_CHOICES, "Prefer the cheapest, fastest, or quickest-to-answer provider."),
    ("allow_fallbacks", "allow fallbacks", YES_NO_CHOICES, "Whether another provider may answer."),
    (
        "data_collection",
        "data collection",
        COLLECTION_CHOICES,
        "Deny to use only providers that do not store or train on requests.",
    ),
)
# The JSON text fields: input, label, and tooltip.
JSON_FIELDS = (
    (
        "provider_options",
        "provider options",
        "A JSON object of fields for one provider, keyed by its slug. The model's page on OpenRouter lists them.",
    ),
    ("extra_fields", "extra fields", "A JSON object of request fields, added to the body as they are written."),
)
# The provider lists: input and tooltip.
PROVIDER_LISTS = (
    ("order", "Providers to try first, in this order."),
    ("only", "Use only these providers."),
    ("ignore", "Never use these providers."),
)
SLUG_TOOLTIP = "Slugs such as google-vertex, separated by commas. The model's page on OpenRouter lists them."


def _read_providers(text: str) -> tuple[str, ...]:
    """Split a comma-separated provider list, checking each slug and the count."""
    slugs = tuple(slug.strip() for slug in text.split(",") if slug.strip())
    if len(slugs) > MAX_PROVIDERS or any(PROVIDER.match(slug) is None for slug in slugs):
        raise OpenRouterError(ErrorCode.INVALID_INPUT, PROVIDER_SLUG.format(maximum=MAX_PROVIDERS))
    return slugs


def _read_fields(text: str, field: str) -> dict[str, Json]:
    """Read a JSON object field, or nothing when it is empty."""
    if not text.strip():
        return {}
    if len(text.encode()) > MAX_OPTION_BYTES:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, OPTIONS_SIZE.format(field=field))
    try:
        value = parse_json(text, max_bytes=MAX_OPTION_BYTES)
    except OpenRouterError:
        value = None
    if not isinstance(value, dict):
        raise OpenRouterError(ErrorCode.INVALID_INPUT, OPTIONS_JSON.format(field=field))
    return value


class RequestOptions(io.ComfyNode):
    """Output provider routing and extra fields; the paid node refuses what its endpoint does not accept."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Offer every routing field, price cap, and passthrough field OpenRouter accepts."""
        providers = [
            io.String.Input(name, default="", tooltip=f"{tooltip} {SLUG_TOOLTIP}") for name, tooltip in PROVIDER_LISTS
        ]
        routing = [
            io.Combo.Input(name, display_name=label, options=list(choices), default=MODEL_DEFAULT, tooltip=tooltip)
            for name, label, choices, tooltip in ROUTING_CHOICES
        ]
        prices = [
            io.Float.Input(
                name,
                display_name=f"max {kind} price",
                default=0.0,
                min=0.0,
                max=1000.0,
                step=0.01,
                advanced=True,
                tooltip=f"Skip providers that charge more than this, in USD per 1M {kind} tokens; 0 sets no cap.",
            )
            for name, kind in (("max_prompt_price", "prompt"), ("max_completion_price", "completion"))
        ]
        fields = [
            io.String.Input(name, display_name=label, multiline=True, default="", advanced=True, tooltip=tooltip)
            for name, label, tooltip in JSON_FIELDS
        ]
        zdr = io.Boolean.Input(
            "zdr",
            display_name="zero data retention",
            default=False,
            tooltip="Use only providers with zero data retention.",
        )
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Request Options",
            category=SHARED_MENU,
            description="Choose providers, price caps, and extra request fields for any OpenRouter node.",
            inputs=[*providers, *routing, zdr, *prices, *fields],
            outputs=[io.Custom(OPTIONS_TYPE).Output("options", display_name="options")],
        )

    @classmethod
    @override
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls,
        *,
        order: str,
        only: str,
        ignore: str,
        sort: str,
        allow_fallbacks: str,
        data_collection: str,
        zdr: bool,
        max_prompt_price: float,
        max_completion_price: float,
        provider_options: str,
        extra_fields: str,
    ) -> io.NodeOutput:
        """Check each field before any request; the endpoint checks happen when a paid node merges them."""
        per_provider = _read_fields(provider_options, "provider options")
        if any(PROVIDER.match(slug) is None for slug in per_provider):
            raise OpenRouterError(ErrorCode.INVALID_INPUT, PROVIDER_SLUG.format(maximum=MAX_PROVIDERS))
        prices = {"prompt": max_prompt_price, "completion": max_completion_price}
        options = OptionsRecord(
            order=_read_providers(order),
            only=_read_providers(only),
            ignore=_read_providers(ignore),
            sort=sort if sort != MODEL_DEFAULT else None,
            allow_fallbacks={"yes": True, "no": False}.get(allow_fallbacks),
            data_collection=data_collection if data_collection != MODEL_DEFAULT else None,
            zdr=True if zdr else None,
            max_price=MappingProxyType(
                {
                    line: format(Decimal(str(price)).quantize(Decimal("0.000001")).normalize(), "f")
                    for line, price in prices.items()
                    if price > 0
                }
            ),
            provider_options=MappingProxyType(per_provider),
            extra_fields=MappingProxyType(_read_fields(extra_fields, "extra fields")),
        )
        return io.NodeOutput(options)


__all__ = ["RequestOptions"]
