"""Private credential values with redacted representations."""

from dataclasses import field, dataclass


@dataclass(frozen=True, slots=True)
class Credential:
    """A secret that only a request to OpenRouter reads.

    Attributes:
        value: Validated secret; the dataclass representation leaves it out.

    """

    value: str = field(repr=False)


__all__ = ['Credential']
