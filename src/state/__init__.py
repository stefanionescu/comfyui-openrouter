"""Records shared by the runtime: dataclasses for in-process values, pydantic models for JSON."""

from pydantic import BaseModel, ConfigDict


type Json = bool | int | float | str | list[Json] | dict[str, Json] | None


class Value(BaseModel):
    """A frozen record that refuses unknown fields, for files this extension writes."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Reply(BaseModel):
    """A frozen record that ignores unknown fields, for documents OpenRouter sends."""

    # OpenRouter adds fields over time; a new field must not break a paid run that already succeeded.
    model_config = ConfigDict(extra="ignore", frozen=True)


# Type aliases are imported by name; __all__ lists runtime names.
__all__ = ["Reply", "Value"]
