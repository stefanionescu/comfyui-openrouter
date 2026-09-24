"""Validate private limits before any request is sent."""

from ..state import Json
from dataclasses import fields
from ..state.settings import Settings
from ..errors import ErrorCode, ConnectorError
from ..config.settings import INTEGER_SETTINGS, DEFAULT_MODEL_AUTO_CHECK
from ..config.messages.settings import SETTINGS_RANGE, SETTINGS_ON_OFF, SETTING_UNKNOWN, SETTINGS_WHOLE_NUMBERS


# The configured default for every setting.
DEFAULT_SETTINGS = Settings(
    **{name: definition["default"] for name, definition in INTEGER_SETTINGS.items()},
    model_auto_check=DEFAULT_MODEL_AUTO_CHECK,
)


def validate_settings(settings: Settings) -> None:
    """Keep every limit in its range."""
    for name, definition in INTEGER_SETTINGS.items():
        value: int = getattr(settings, name)
        if not definition["minimum"] <= value <= definition["maximum"]:
            raise ConnectorError(ErrorCode.CONFIGURATION, SETTINGS_RANGE)


def parse_settings(document: dict[str, Json]) -> Settings:
    """Reject unknown settings instead of silently accepting misspelled limits."""
    expected = {item.name for item in fields(Settings)}
    if document.keys() - expected:
        raise ConnectorError(ErrorCode.CONFIGURATION, SETTING_UNKNOWN)
    defaults = DEFAULT_SETTINGS
    integers: dict[str, int] = {}
    for name in expected - {"model_auto_check"}:
        value = document.get(name, getattr(defaults, name))
        if type(value) is not int:
            raise ConnectorError(ErrorCode.CONFIGURATION, SETTINGS_WHOLE_NUMBERS)
        integers[name] = value
    automatic = document.get("model_auto_check", defaults.model_auto_check)
    if not isinstance(automatic, bool):
        raise ConnectorError(ErrorCode.CONFIGURATION, SETTINGS_ON_OFF)
    settings = Settings(**integers, model_auto_check=automatic)
    validate_settings(settings)
    return settings


__all__ = ["DEFAULT_SETTINGS", "parse_settings", "validate_settings"]
