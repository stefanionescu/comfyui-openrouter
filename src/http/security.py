"""Restrict private configuration routes to the local ComfyUI origin."""

import ipaddress
from aiohttp import web
from typing import cast
from urllib.parse import SplitResult, urlsplit
from ..config.messages.requests import LOCAL_CONNECTION_REQUIRED


def _is_local_target(request: web.Request, target: SplitResult, port: int) -> bool:
    """Match a loopback peer and a bare loopback URL, without user information or suffixes, to the server socket."""
    peer = ipaddress.ip_address(request.remote or "")
    socket = request.transport.get_extra_info("sockname") if request.transport else None
    address = cast("tuple[object, ...]", socket) if isinstance(socket, tuple) else ()
    socket_port = address[1] if len(address) > 1 else None
    is_local_url = all(
        (
            target.hostname in {"localhost", "127.0.0.1", "::1"},
            target.username is None,
            target.password is None,
            not target.path,
            not target.query,
            not target.fragment,
        )
    )
    return peer.is_loopback and is_local_url and port == socket_port


def _is_same_origin(origin: str, target: SplitResult, port: int) -> bool:
    """Accept only an origin with the request's exact scheme, host, and effective port."""
    source = urlsplit(origin)
    source_port = source.port or (443 if source.scheme == "https" else 80)
    return all(
        (
            source.scheme == target.scheme,
            source.hostname == target.hostname,
            source_port == port,
            source.path in ("", "/"),
            source.username is None,
            source.password is None,
            not source.query,
            not source.fragment,
        )
    )


def require_local_request(request: web.Request, *, is_mutation: bool, is_multi_user: bool) -> None:
    """Reject remote peers, rebinding hosts, cross-origin requests, and unsafe writes."""
    forbidden = web.HTTPForbidden(text=LOCAL_CONNECTION_REQUIRED)
    try:
        # Private routes require a direct local connection, so proxy metadata is refused.
        if any(
            name.lower() in {"forwarded", "x-real-ip"} or name.lower().startswith("x-forwarded-")
            for name in request.headers
        ):
            raise forbidden
        target = urlsplit(f"{request.scheme}://{request.host}")
        port = target.port or (443 if request.secure else 80)
        if not _is_local_target(request, target, port):
            raise forbidden
        origin = request.headers.get("Origin")
        if origin is not None and not _is_same_origin(origin, target, port):
            raise forbidden
        if request.headers.get("Sec-Fetch-Site") in {"cross-site", "same-site"}:
            raise forbidden
        if is_mutation and (is_multi_user or request.headers.get("X-OpenRouter-Comfy") != "1"):
            raise forbidden
    except ValueError:
        raise forbidden from None


__all__ = ["require_local_request"]
