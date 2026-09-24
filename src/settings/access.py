"""Serve the private settings routes only to the local ComfyUI page, with safe errors and private headers."""

import ipaddress
from aiohttp import web
from typing import cast
from ..types import Json
from http import HTTPStatus
from urllib.parse import SplitResult, urlsplit
from collections.abc import Callable, Awaitable
from ..types.errors import ErrorCode, OpenRouterError
from ..config.messages.settings import STATE_UNREADABLE
from ..config.messages.requests import LOCAL_CONNECTION_REQUIRED
from ..config.security import (
    HTTP_PORT,
    HTTPS_PORT,
    LOCAL_HOSTS,
    CHANGE_HEADER,
    PROXY_HEADERS,
    PRIVATE_HEADERS,
    CROSS_SITE_FETCHES,
    PROXY_HEADER_PREFIX,
)


def _is_local_target(request: web.Request, target: SplitResult, port: int) -> bool:
    """Match a loopback peer and a bare loopback URL, without user information or suffixes, to the server socket."""
    peer = ipaddress.ip_address(request.remote or "")
    socket = request.transport.get_extra_info("sockname") if request.transport else None
    address = cast("tuple[object, ...]", socket) if isinstance(socket, tuple) else ()
    socket_port = address[1] if len(address) > 1 else None
    is_local_url = all(
        (
            target.hostname in LOCAL_HOSTS,
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
    source_port = source.port or (HTTPS_PORT if source.scheme == "https" else HTTP_PORT)
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


def _validate_local_request(request: web.Request, *, is_mutation: bool, is_multi_user: bool) -> None:
    """Reject remote peers, rebinding hosts, cross-origin requests, and unsafe writes."""
    forbidden = web.HTTPForbidden(text=LOCAL_CONNECTION_REQUIRED)
    try:
        # Private routes require a direct local connection, so proxy metadata is refused.
        if any(
            name.lower() in PROXY_HEADERS or name.lower().startswith(PROXY_HEADER_PREFIX) for name in request.headers
        ):
            raise forbidden
        target = urlsplit(f"{request.scheme}://{request.host}")
        port = target.port or (HTTPS_PORT if request.secure else HTTP_PORT)
        if not _is_local_target(request, target, port):
            raise forbidden
        origin = request.headers.get("Origin")
        if origin is not None and not _is_same_origin(origin, target, port):
            raise forbidden
        if request.headers.get("Sec-Fetch-Site") in CROSS_SITE_FETCHES:
            raise forbidden
        if is_mutation and (is_multi_user or request.headers.get(CHANGE_HEADER) != "1"):
            raise forbidden
    except ValueError:
        raise forbidden from None


def build_local_route(
    callback: Callable[[web.Request], Awaitable[dict[str, Json]]],
    *,
    is_mutation: bool,
    is_multi_user: bool,
) -> Callable[[web.Request], Awaitable[web.Response]]:
    """Wrap a route with local-owner checks, safe errors, and private response headers."""

    async def build_response(request: web.Request) -> web.Response:
        """Authorize the request and return only the route's public result or safe error."""
        try:
            _validate_local_request(request, is_mutation=is_mutation, is_multi_user=is_multi_user)
            return web.json_response(await callback(request), headers=PRIVATE_HEADERS)
        except OpenRouterError as error:
            # A stale revision is a conflict the page resolves by reloading; every other failure is a bad request.
            message, status = (
                str(error),
                HTTPStatus.CONFLICT if error.code is ErrorCode.CONFLICT else HTTPStatus.BAD_REQUEST,
            )
        except web.HTTPException as error:
            message, status = error.text, error.status
        except (OSError, UnicodeError):
            message, status = STATE_UNREADABLE, HTTPStatus.INTERNAL_SERVER_ERROR
        return web.json_response({"error": message}, status=status, headers=PRIVATE_HEADERS)

    return build_response


__all__ = ["build_local_route"]
