"""List resources use case handler."""

import structlog

from content_resource_api.application.commands import ListResourcesCommand
from content_resource_api.application.results import ResourceListItem, ResourceListResult
from content_resource_api.domain.authorization import AuthorizationService
from content_resource_api.domain.models import ClientPrincipal
from content_resource_api.domain.values import CategoryName
from content_resource_api.ports.registry import ResourceRegistryPort

log = structlog.get_logger(__name__)


class ListResourcesHandler:
    def __init__(self, registry: ResourceRegistryPort, auth_service: AuthorizationService) -> None:
        self._registry = registry
        self._auth = auth_service

    def handle(self, command: ListResourcesCommand) -> ResourceListResult:
        principal = ClientPrincipal(
            client_id=command.principal_id,
            scopes=command.principal_scopes,
        )
        resources = self._registry.list_resources(CategoryName(command.category))
        items = []
        for resource in resources:
            decision = self._auth.authorize(principal, resource)
            if not decision.allowed:
                continue
            items.append(ResourceListItem(
                name=resource.public_filename,
                path=f"/{resource.category}/{resource.public_filename}",
            ))
        return ResourceListResult(items=tuple(items))
