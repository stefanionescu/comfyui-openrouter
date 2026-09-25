"""Define editable settings, their units, defaults, and supported ranges."""

SETTING_RANGES: dict[str, dict[str, int]] = {
    "request_timeout_seconds": {"default": 600, "minimum": 10, "maximum": 3600},
    "max_upload_megabytes": {"default": 64, "minimum": 1, "maximum": 512},
    "max_download_megabytes": {"default": 512, "minimum": 16, "maximum": 4096},
    "video_check_interval_seconds": {"default": 15, "minimum": 5, "maximum": 120},
    "video_wait_minutes": {"default": 30, "minimum": 1, "maximum": 240},
    "identical_video_block_minutes": {"default": 30, "minimum": 5, "maximum": 1440},
}

MAX_SETTINGS_BYTES = 4096


SETTINGS_TIMEOUT_SECONDS = 5

REQUEST_CHUNK_BYTES = 1024

__all__ = [
    "MAX_SETTINGS_BYTES",
    "REQUEST_CHUNK_BYTES",
    "SETTINGS_TIMEOUT_SECONDS",
    "SETTING_RANGES",
]
