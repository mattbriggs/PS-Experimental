"""Test double for ContentRepositoryPort."""

from collections.abc import AsyncIterator

from content_resource_api.domain.enums import DependencyState
from content_resource_api.domain.models import DependencyStatus, ResourceMetadata
from content_resource_api.domain.values import UpstreamResourceRef


class FakeContentRepository:
    def __init__(
        self,
        metadata: ResourceMetadata | None = None,
        content: bytes = b"fake content",
        available: bool = True,
    ) -> None:
        self._metadata = metadata or ResourceMetadata(
            etag='"abc123"',
            content_type="application/xml",
            content_length=len(content),
        )
        self._content = content
        self._available = available

    async def get_metadata(self, resource_ref: UpstreamResourceRef) -> ResourceMetadata:
        return self._metadata

    async def open_stream(self, resource_ref: UpstreamResourceRef) -> AsyncIterator[bytes]:
        return self._stream()

    async def _stream(self) -> AsyncIterator[bytes]:
        yield self._content

    async def check_availability(self) -> DependencyStatus:
        state = DependencyState.HEALTHY if self._available else DependencyState.UNAVAILABLE
        return DependencyStatus(name="webdav", state=state)
