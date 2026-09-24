"""Private credential values with redacted representations."""

from dataclasses import field, dataclass


@dataclass(frozen=True, slots=True, repr=False)
class Credential:
    """A secret revealed explicitly at the OpenRouter boundary.

    Attributes:
        _value: Validated secret excluded from representations.

    """

    _value: str = field(repr=False)

    def __repr__(self) -> str:
        """Identify the credential type without revealing its value."""
        return "Credential(<redacted>)"

    def __str__(self) -> str:
        """Return a redacted label instead of the credential value."""
        return "<redacted>"

    def reveal(self) -> str:
        """Return the secret only for an authorized OpenRouter request."""
        return self._value


__all__ = ["Credential"]
