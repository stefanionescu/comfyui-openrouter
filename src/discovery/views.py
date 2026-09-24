"""Describe each saved model for the models dialog: its nodes, prices, and model page."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from .choices import build_choices
from ..config.discovery import (
    ENDPOINT_NODES,
    MODEL_PAGE_URL,
    VIDEO_PRICE_UNIT,
    TOKEN_PRICE_UNITS,
    SPEECH_PRICE_UNITS,
)

if TYPE_CHECKING:
    from ..state import Json
    from ..state.models import Snapshot
    from collections.abc import Mapping, Sequence

# Endpoints whose models are priced per token.
TOKEN_ENDPOINTS = frozenset({"chat", "embeddings", "rerank", "decisions"})


def build_model_views(snapshot: Snapshot) -> list[Json]:
    """List every saved model, newest first, with the nodes that list it and its documented prices."""
    endpoints: dict[str, list[str]] = {}
    for endpoint, choices in build_choices(snapshot).items():
        for model_id in choices:
            endpoints.setdefault(model_id, []).append(endpoint)
    videos = {record.id: record.prices for record in snapshot.videos}
    rows: list[Json] = []
    for record in sorted(snapshot.models, key=lambda item: (-item.created, item.id)):
        served = endpoints.get(record.id, [])
        prices = _price_lines(record.prices, served)
        if record.id in videos:
            prices += _video_price_lines(videos[record.id])
        rows.append(
            {
                "id": record.id,
                "name": record.name,
                "nodes": [ENDPOINT_NODES[endpoint] for endpoint in served],
                "observed": record.is_observed,
                "documentation_url": MODEL_PAGE_URL.format(model_id=record.id),
                "prices": prices,
            }
        )
    return rows


def _price_lines(prices: Mapping[str, str], served: Sequence[str]) -> list[Json]:
    """Keep the token or character price lines of a model the nodes price that way, leaving out zero prices."""
    units: Mapping[str, str] = {}
    if TOKEN_ENDPOINTS.intersection(served):
        units = TOKEN_PRICE_UNITS
    elif "speech" in served:
        units = SPEECH_PRICE_UNITS
    return [
        {"label": line, "usd": prices[line], "unit": unit}
        for line, unit in units.items()
        if line in prices and Decimal(prices[line]) > 0
    ]


def _video_price_lines(prices: Mapping[str, str]) -> list[Json]:
    """Read video SKUs: dollars or cents per video second, and other SKUs without a unit a person can estimate with."""
    lines: list[Json] = []
    for sku, price in sorted(prices.items()):
        amount = Decimal(price)
        if amount <= 0:
            continue
        if "duration_seconds" in sku:
            lines.append({"label": sku, "usd": price, "unit": VIDEO_PRICE_UNIT})
        elif sku.startswith("cents_per") and "second" in sku:
            lines.append({"label": sku, "usd": format((amount / 100).normalize(), "f"), "unit": VIDEO_PRICE_UNIT})
        else:
            lines.append({"label": sku, "usd": price, "unit": None})
    return lines


__all__ = ["build_model_views"]
