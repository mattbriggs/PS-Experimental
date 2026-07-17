"""Result types returned from application handlers."""

from collections.abc import AsyncIterator

from pydantic import BaseModel

from content_resource_api.domain.models import RegisteredResource, ResourceMetadata


class ResourceListItem(BaseModel):
    model_config = {"frozen": True}
    name: str
    path: str
    contentType: str | None = None
    size: int | None = None


class ResourceListResult(BaseModel):
    model_config = {"frozen": True}
    items: tuple[ResourceListItem, ...]


class NotModifiedResult(BaseModel):
    model_config = {"frozen": True}
    etag: str | None = None


class ResourceStreamResult:
    """Holds metadata and a streaming body."""
    def __init__(
        self,
        metadata: ResourceMetadata,
        resource: RegisteredResource,
        stream: AsyncIterator[bytes],
    ) -> None:
        self.metadata = metadata
        self.resource = resource
        self.stream = stream
