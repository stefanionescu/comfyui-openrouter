"""The local settings API: its routes, the requests it accepts, and the headers it sends."""

STATUS_ROUTE = "/openrouter/v1/status"
SETTINGS_ROUTE = "/openrouter/v1/settings"
CREDENTIAL_ROUTE = "/openrouter/v1/credential"
JSON_MEDIA_TYPE = "application/json"
MAX_JSON_BYTES = 1_048_576
MAX_JSON_DEPTH = 16
MAX_CREDENTIAL_CHARACTERS = 1024
# The bytes of the random token that renews ComfyUI's cache when the key changes.
GENERATION_TOKEN_BYTES = 16
PRIVATE_HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}
# A private route answers only a direct connection to a loopback host, on the server's own port.
LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1")
HTTP_PORT = 80
HTTPS_PORT = 443
# Proxy metadata means the connection is not direct, so a request carrying it is refused.
PROXY_HEADERS = ("forwarded", "x-real-ip")
PROXY_HEADER_PREFIX = "x-forwarded-"
CROSS_SITE_FETCHES = ("cross-site", "same-site")
# The settings dialog sends this header with every change; a plain form or link cannot.
CHANGE_HEADER = "X-OpenRouter-Comfy"

__all__ = [
    "CHANGE_HEADER",
    "CREDENTIAL_ROUTE",
    "CROSS_SITE_FETCHES",
    "GENERATION_TOKEN_BYTES",
    "HTTPS_PORT",
    "HTTP_PORT",
    "JSON_MEDIA_TYPE",
    "LOCAL_HOSTS",
    "MAX_CREDENTIAL_CHARACTERS",
    "MAX_JSON_BYTES",
    "MAX_JSON_DEPTH",
    "PRIVATE_HEADERS",
    "PROXY_HEADERS",
    "PROXY_HEADER_PREFIX",
    "SETTINGS_ROUTE",
    "STATUS_ROUTE",
]
