"""Provider routing and extra fields from a Request Options node."""

from . import Json
from dataclasses import dataclass
from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class RequestOptions:
    """Provider routing and extra fields to merge into one request.

    Attributes:
        order: Provider slugs to try first, in order.
        only: The only provider slugs allowed.
        ignore: Provider slugs never used.
        sort: How OpenRouter orders providers, or None for its default.
        allow_fallbacks: Whether another provider may answer, or None for the default.
        data_collection: "allow" or "deny", or None for the account setting.
        zdr: True to require zero data retention, or None.
        max_price: Price caps in US dollars per million tokens, as decimal text.
        provider_options: Provider-specific fields keyed by provider slug.
        extra_fields: Top-level request fields added to the body.

    """

    order: tuple[str, ...]
    only: tuple[str, ...]
    ignore: tuple[str, ...]
    sort: str | None
    allow_fallbacks: bool | None
    data_collection: str | None
    zdr: bool | None
    max_price: Mapping[str, str]
    provider_options: Mapping[str, Json]
    extra_fields: Mapping[str, Json]


__all__ = ["RequestOptions"]
