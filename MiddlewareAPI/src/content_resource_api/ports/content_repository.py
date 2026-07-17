"""Content repository port protocol."""

from collections.abc import AsyncIterator
from typing import Protocol

from content_resource_api.domain.models import DependencyStatus, ResourceMetadata
from content_resource_api.domain.values import UpstreamResourceRef


class ContentRepositoryPort(Protocol):
    """Read-only access to upstream content."""

    async def get_metadata(self, resource_ref: UpstreamResourceRef) -> ResourceMetadata:
        ...

    async def open_stream(self, resource_ref: UpstreamResourceRef) -> AsyncIterator[bytes]:
        ...

    async def check_availability(self) -> DependencyStatus:
        ...
