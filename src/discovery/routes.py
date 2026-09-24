"""Let the local ComfyUI owner read, refresh, and roll back the saved model list."""

import re
import asyncio
from aiohttp import web
from ..state import Json
from .store import ModelStore
from .checker import ModelChecker
from ..http.guard import local_route
from ..http.request import read_document
from ..config.security import MODELS_PREFIX
from ..config.patterns import REVISION_PATTERN
from ..config.messages.models import REFRESH_BODY, MODEL_REVISION_REQUIRED

REVISION = re.compile(REVISION_PATTERN)


class ModelRoutes:
    """Local-owner endpoints for the model list, its refresh, and its rollback."""

    def __init__(self, store: ModelStore, *, is_multi_user: bool, checker: ModelChecker) -> None:
        """Bind the model store and the scheduled checker."""
        self.store = store
        self.is_multi_user = is_multi_user
        self.checker = checker

    def _add_route_fields(self, result: dict[str, Json]) -> dict[str, Json]:
        """Add the change permission and the last scheduled check, relative to the revision the reply shows."""
        checker, revision = self.checker, result["revision"]
        is_comparable = checker.base_revision == revision and checker.candidate_revision is not None
        result["mutation_allowed"] = not self.is_multi_user
        result["automatic_check"] = {
            "enabled": checker.enabled,
            "interval_hours": checker.interval_hours,
            "running": checker.running,
            "checked_at": checker.checked_at,
            "update_available": checker.candidate_revision != revision if is_comparable else None,
            "error": checker.error,
        }
        return result

    async def status(self, _request: web.Request) -> dict[str, Json]:
        """Read the saved model list without blocking the host event loop."""
        return self._add_route_fields(await asyncio.to_thread(self.store.status))

    async def refresh(self, request: web.Request) -> dict[str, Json]:
        """Refresh the public lists and return the newly saved model list."""
        if request.can_read_body:
            raise web.HTTPBadRequest(text=REFRESH_BODY)
        return self._add_route_fields(await self.store.refresh())

    async def rollback(self, request: web.Request) -> dict[str, Json]:
        """Restore the previous list only if the caller still has the current revision."""
        body = await read_document(request)
        revision = body.get("revision")
        if body.keys() != {"revision"} or not isinstance(revision, str) or not REVISION.match(revision):
            raise web.HTTPBadRequest(text=MODEL_REVISION_REQUIRED)
        return self._add_route_fields(await asyncio.to_thread(self.store.rollback, revision))

    def register(self, routes: web.RouteTableDef) -> None:
        """Register the model routes with local-owner and change guards."""
        policy = {"is_multi_user": self.is_multi_user}
        routes.get(MODELS_PREFIX)(local_route(self.status, is_mutation=False, **policy))
        routes.post(MODELS_PREFIX + "/refresh")(local_route(self.refresh, is_mutation=True, **policy))
        routes.post(MODELS_PREFIX + "/rollback")(local_route(self.rollback, is_mutation=True, **policy))


__all__ = ["ModelRoutes"]
