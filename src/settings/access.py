"""Serve the private settings routes only to the local ComfyUI page, with safe errors and private headers."""

import ipaddress
from aiohttp import web
from typing import cast
from ..types import Json
from ..config.security import PRIVATE_HEADERS
from urllib.parse import SplitResult, urlsplit
from collections.abc import Callable, Awaitable
from ..types.errors import ErrorCode, OpenRouterError
from ..config.messages.settings import STATE_UNREADABLE
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


def _require_local_request(request: web.Request, *, is_mutation: bool, is_multi_user: bool) -> None:
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


def local_route(
    callback: Callable[[web.Request], Awaitable[dict[str, Json]]],
    *,
    is_mutation: bool,
    is_multi_user: bool,
) -> Callable[[web.Request], Awaitable[web.Response]]:
    """Wrap a route with local-owner checks, safe errors, and private response headers."""

    async def respond(request: web.Request) -> web.Response:
        """Authorize the request and return only the route's public result or safe error."""
        try:
            _require_local_request(request, is_mutation=is_mutation, is_multi_user=is_multi_user)
            return web.json_response(await callback(request), headers=PRIVATE_HEADERS)
        except OpenRouterError as error:
            # A stale revision is a conflict the page resolves by reloading; every other failure is a bad request.
            message, status = str(error), 409 if error.code is ErrorCode.CONFLICT else 400
        except web.HTTPException as error:
            message, status = error.text, error.status
        except (OSError, UnicodeError):
            message, status = STATE_UNREADABLE, 500
        return web.json_response({"error": message}, status=status, headers=PRIVATE_HEADERS)

    return respond


__all__ = ["local_route"]
