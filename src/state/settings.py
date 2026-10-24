"""Execution settings and private configuration snapshot records."""

from dataclasses import field, dataclass

from .credentials import Credential


@dataclass(frozen=True, slots=True)
class Settings:
    """Limits that a workflow cannot raise.

    Attributes:
        request_timeout_seconds: How long one generation may take; for a video, the whole job.
        max_upload_megabytes: Largest encoded media in one request.
        max_download_megabytes: Largest reply body, image, audio, or video accepted.

    """

    request_timeout_seconds: int
    max_upload_megabytes: int
    max_download_megabytes: int


@dataclass(frozen=True, slots=True)
class Configuration:
    """One private settings and credential snapshot for one paid request.

    Attributes:
        settings: Effective execution limits.
        credential: Private OpenRouter key excluded from representations.
        generation: Token identifying the effective execution configuration.

    """

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str


__all__ = ['Configuration', 'Settings']
