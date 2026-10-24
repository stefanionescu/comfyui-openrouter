"""Serve private settings and key changes through guarded local routes."""

import re
import asyncio
from dataclasses import field, dataclass

from aiohttp import web

from .body import read_body
from .store import ConfigurationStore
from ..state import Json
from .access import build_local_route
from ..state.parsing import validate_fields
from ..config.patterns import REVISION_PATTERN
from ..config.security import ROUTES
from ..config.messages.requests import CLEAR_KEY_BODY, SINGLE_KEY_REQUIRED, SETTINGS_REVISION_REQUIRED

REVISION = re.compile(REVISION_PATTERN)


@dataclass(frozen=True, slots=True)
class ConfigurationRoutes:
    """Register routes once during the host's extension load phase.

    Attributes:
        store: The configuration store.
        is_multi_user: The host's multi-user access policy, which allows no changes.

    """

    store: ConfigurationStore
    is_multi_user: bool = field(default=False, kw_only=True)

    async def save_settings(self, request: web.Request) -> dict[str, Json]:
        """Validate a settings patch and save it against the caller's current revision."""
        document = await read_body(request)
        revision = document.get('revision')
        if document.keys() != {'revision', 'settings'} or not isinstance(revision, str) or not REVISION.match(revision):
            raise web.HTTPBadRequest(text=SETTINGS_REVISION_REQUIRED)
        return await asyncio.to_thread(self.store.save_settings, validate_fields(document['settings']), revision)

    async def save_credential(self, request: web.Request) -> dict[str, Json]:
        """Accept one API key and save it only through the private configuration store."""
        document = await read_body(request)
        if document.keys() != {'api_key'} or not isinstance(document['api_key'], str):
            raise web.HTTPBadRequest(text=SINGLE_KEY_REQUIRED)
        return await asyncio.to_thread(self.store.save_credential, document['api_key'])

    async def delete_credential(self, request: web.Request) -> dict[str, Json]:
        """Remove the saved key after rejecting unexpected request content."""
        if request.can_read_body:
            raise web.HTTPBadRequest(text=CLEAR_KEY_BODY)
        return await asyncio.to_thread(self.store.delete_credential)

    def register(self, routes: web.RouteTableDef) -> None:
        """Register guarded status, settings, key-save, and key-removal endpoints."""
        policy = {'is_multi_user': self.is_multi_user}
        read_status = build_local_route(
            lambda _request: asyncio.to_thread(self.store.read_status), is_mutation=False, **policy
        )
        routes.get(ROUTES['STATUS'])(read_status)
        routes.patch(ROUTES['SETTINGS'])(build_local_route(self.save_settings, is_mutation=True, **policy))
        routes.put(ROUTES['CREDENTIAL'])(build_local_route(self.save_credential, is_mutation=True, **policy))
        routes.delete(ROUTES['CREDENTIAL'])(build_local_route(self.delete_credential, is_mutation=True, **policy))


__all__ = ['ConfigurationRoutes']
