"""The local settings API: its routes, the requests it accepts, and the replies it sends."""

# The local routes of the settings dialog.
ROUTES = {
    "STATUS": "/openrouter/v1/status",
    "SETTINGS": "/openrouter/v1/settings",
    "CREDENTIAL": "/openrouter/v1/credential",
}

# A private route answers only a direct connection to one of these loopback hosts.
LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1")

# The port a URL without one uses, for checking that a request comes to the server's own port.
DEFAULT_PORTS = {
    "HTTP": 80,
    "HTTPS": 443,
}

# Proxy metadata means the connection is not direct, so a request carrying it is refused.
PROXY_HEADERS = ("forwarded", "x-real-ip")

# Every header under this prefix is proxy metadata too.
PROXY_HEADER_PREFIX = "x-forwarded-"

# A fetch from another site is not the settings dialog, so a change it sends is refused.
CROSS_SITE_FETCHES = ("cross-site", "same-site")

# The settings dialog sends this header with every change; a plain form or link cannot.
CHANGE_HEADER = "X-OpenRouter-Comfy"

# Every reply is JSON.
JSON_MEDIA_TYPE = "application/json"

# Browsers neither cache a reply nor reinterpret its type.
PRIVATE_HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}

# JSON the extension reads is refused beyond this size and depth.
JSON_LIMITS = {
    "MAX_BYTES": 1_048_576,
    "MAX_DEPTH": 16,
}

# A key is refused beyond this length.
MAX_CREDENTIAL_CHARACTERS = 1024

# The bytes of the random token that renews ComfyUI's cache when the key changes.
GENERATION_TOKEN_BYTES = 16

__all__ = [
    "CHANGE_HEADER",
    "CROSS_SITE_FETCHES",
    "DEFAULT_PORTS",
    "GENERATION_TOKEN_BYTES",
    "JSON_LIMITS",
    "JSON_MEDIA_TYPE",
    "LOCAL_HOSTS",
    "MAX_CREDENTIAL_CHARACTERS",
    "PRIVATE_HEADERS",
    "PROXY_HEADERS",
    "PROXY_HEADER_PREFIX",
    "ROUTES",
]
