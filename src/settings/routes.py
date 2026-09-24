"""Serve private settings and key changes through guarded local routes."""

import re
import asyncio
from aiohttp import web
from ..state import Json
from .access import local_route
from .body import read_document
from .store import ConfigurationStore
from ..state.parsing import mapping_value
from ..config.security import SETTINGS_PREFIX
from ..config.patterns import REVISION_PATTERN
from ..config.messages.requests import CLEAR_KEY_BODY, SINGLE_KEY_REQUIRED, SETTINGS_REVISION_REQUIRED

REVISION = re.compile(REVISION_PATTERN)


class ConfigurationRoutes:
    """Register routes once during the host's extension load phase."""

    def __init__(self, store: ConfigurationStore, *, is_multi_user: bool = False) -> None:
        """Bind the configuration store and the host's multi-user access policy."""
        self.store = store
        self.is_multi_user = is_multi_user

    async def status(self, _request: web.Request) -> dict[str, Json]:
        """Return effective settings and whether the current host permits changes."""
        result = await asyncio.to_thread(self.store.status)
        return result | {"mutation_allowed": not self.is_multi_user}

    async def settings(self, request: web.Request) -> dict[str, Json]:
        """Validate a settings patch and save it against the caller's current revision."""
        document = await read_document(request)
        revision = document.get("revision")
        if document.keys() != {"revision", "settings"} or not isinstance(revision, str) or not REVISION.match(revision):
            raise web.HTTPBadRequest(text=SETTINGS_REVISION_REQUIRED)
        result = await asyncio.to_thread(self.store.update_settings, mapping_value(document["settings"]), revision)
        return result | {"mutation_allowed": not self.is_multi_user}

    async def credential(self, request: web.Request) -> dict[str, Json]:
        """Accept one API key and save it only through the private configuration store."""
        document = await read_document(request)
        if document.keys() != {"api_key"} or not isinstance(document["api_key"], str):
            raise web.HTTPBadRequest(text=SINGLE_KEY_REQUIRED)
        result = await asyncio.to_thread(self.store.save_credential, document["api_key"])
        return result | {"mutation_allowed": not self.is_multi_user}

    async def clear_credential(self, request: web.Request) -> dict[str, Json]:
        """Remove the saved key after rejecting unexpected request content."""
        if request.can_read_body:
            raise web.HTTPBadRequest(text=CLEAR_KEY_BODY)
        result = await asyncio.to_thread(self.store.clear_credential)
        return result | {"mutation_allowed": not self.is_multi_user}

    def register(self, routes: web.RouteTableDef) -> None:
        """Register guarded status, settings, key-save, and key-removal endpoints."""
        policy = {"is_multi_user": self.is_multi_user}
        routes.get(SETTINGS_PREFIX + "/status")(local_route(self.status, is_mutation=False, **policy))
        routes.patch(SETTINGS_PREFIX + "/settings")(local_route(self.settings, is_mutation=True, **policy))
        routes.put(SETTINGS_PREFIX + "/credential")(local_route(self.credential, is_mutation=True, **policy))
        routes.delete(SETTINGS_PREFIX + "/credential")(local_route(self.clear_credential, is_mutation=True, **policy))


__all__ = ["ConfigurationRoutes"]
