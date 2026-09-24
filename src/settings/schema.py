"""Validate private limits before any request is sent."""

from ..types import Json
from dataclasses import fields
from ..types.settings import Settings
from ..config.settings import SETTING_RANGES
from ..types.errors import ErrorCode, OpenRouterError
from ..config.messages.settings import SETTINGS_RANGE, SETTING_UNKNOWN, SETTINGS_WHOLE_NUMBERS


# The configured default for every setting.
DEFAULT_SETTINGS = Settings(**{name: definition["default"] for name, definition in SETTING_RANGES.items()})


def _validate_settings(settings: Settings) -> None:
    """Keep every limit in its range."""
    for name, definition in SETTING_RANGES.items():
        value: int = getattr(settings, name)
        if not definition["minimum"] <= value <= definition["maximum"]:
            raise OpenRouterError(ErrorCode.CONFIGURATION, SETTINGS_RANGE)


def parse_settings(document: dict[str, Json]) -> Settings:
    """Reject unknown settings instead of silently accepting misspelled limits."""
    expected = {item.name for item in fields(Settings)}
    if document.keys() - expected:
        raise OpenRouterError(ErrorCode.CONFIGURATION, SETTING_UNKNOWN)
    integers: dict[str, int] = {}
    for name in expected:
        value = document.get(name, getattr(DEFAULT_SETTINGS, name))
        if type(value) is not int:
            raise OpenRouterError(ErrorCode.CONFIGURATION, SETTINGS_WHOLE_NUMBERS)
        integers[name] = value
    settings = Settings(**integers)
    _validate_settings(settings)
    return settings


__all__ = ["DEFAULT_SETTINGS", "parse_settings"]
