"""Health evaluation use case."""

from content_resource_api.application.commands import EvaluateHealthQuery
from content_resource_api.domain.enums import DependencyState
from content_resource_api.domain.models import HealthResult
from content_resource_api.ports.content_repository import ContentRepositoryPort


class EvaluateHealthHandler:
    def __init__(
        self,
        repository: ContentRepositoryPort | None,
        readiness_requires_webdav: bool,
    ) -> None:
        self._repository = repository
        self._requires_webdav = readiness_requires_webdav

    async def handle(self, query: EvaluateHealthQuery) -> HealthResult:
        live = True
        deps = []

        if self._repository is not None:
            status = await self._repository.check_availability()
            deps.append(status)
            if self._requires_webdav and status.state == DependencyState.UNAVAILABLE:
                ready = False
            else:
                ready = True
        else:
            ready = True

        return HealthResult(live=live, ready=ready, dependencies=tuple(deps))
