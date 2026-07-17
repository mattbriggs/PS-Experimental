"""Get resource use case handler."""

import structlog

from content_resource_api.application.commands import GetResourceCommand
from content_resource_api.application.results import NotModifiedResult, ResourceStreamResult
from content_resource_api.domain.authorization import AuthorizationService
from content_resource_api.domain.conditional_requests import ConditionalRequestService
from content_resource_api.domain.errors import AuthorizationError, ResourceTooLarge
from content_resource_api.domain.models import ClientPrincipal
from content_resource_api.domain.values import CategoryName, PublicFilename, UpstreamResourceRef
from content_resource_api.ports.content_repository import ContentRepositoryPort
from content_resource_api.ports.registry import ResourceRegistryPort

log = structlog.get_logger(__name__)


class GetResourceHandler:
    def __init__(
        self,
        registry: ResourceRegistryPort,
        repository: ContentRepositoryPort,
        auth_service: AuthorizationService,
        cond_service: ConditionalRequestService,
    ) -> None:
        self._registry = registry
        self._repository = repository
        self._auth = auth_service
        self._cond = cond_service

    async def handle(
        self, command: GetResourceCommand
    ) -> ResourceStreamResult | NotModifiedResult:
        principal = ClientPrincipal(
            client_id=command.principal_id,
            scopes=command.principal_scopes,
        )
        resource = self._registry.get_resource(
            CategoryName(command.category), PublicFilename(command.filename)
        )
        decision = self._auth.authorize(principal, resource)
        if not decision.allowed:
            raise AuthorizationError(decision.reason)

        metadata = await self._repository.get_metadata(
            UpstreamResourceRef(resource.upstream_object)
        )

        if (
            metadata.content_length is not None
            and metadata.content_length > resource.size_limit_bytes
        ):
            raise ResourceTooLarge(
                f"Resource {resource.public_filename} exceeds size limit "
                f"({metadata.content_length} > {resource.size_limit_bytes})",
                safe_detail="Resource exceeds maximum allowed size",
            )

        cache_decision = self._cond.evaluate(
            metadata,
            command.if_none_match,
            command.if_modified_since,
        )

        if cache_decision.not_modified:
            return NotModifiedResult(etag=cache_decision.etag)

        stream = await self._repository.open_stream(
            UpstreamResourceRef(resource.upstream_object)
        )
        return ResourceStreamResult(metadata=metadata, resource=resource, stream=stream)
