"""Apply the same local access and safe error rules to the extension's routes."""

from aiohttp import web
from ..state import Json
from .security import require_local_request
from ..config.security import PRIVATE_HEADERS
from ..errors import ErrorCode, ConnectorError
from collections.abc import Callable, Awaitable
from ..config.messages.settings import STATE_UNREADABLE


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
            require_local_request(request, is_mutation=is_mutation, is_multi_user=is_multi_user)
            return web.json_response(await callback(request), headers=PRIVATE_HEADERS)
        except ConnectorError as error:
            # A stale revision is a conflict the page resolves by reloading; every other failure is a bad request.
            message, status = str(error), 409 if error.code is ErrorCode.CONFLICT else 400
        except web.HTTPException as error:
            message, status = error.text, error.status
        except (OSError, UnicodeError):
            message, status = STATE_UNREADABLE, 500
        return web.json_response({"error": message}, status=status, headers=PRIVATE_HEADERS)

    return respond


__all__ = ["local_route"]
