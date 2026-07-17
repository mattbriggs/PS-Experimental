"""Resource registry port protocol."""

from typing import Protocol

from content_resource_api.domain.models import RegisteredResource
from content_resource_api.domain.values import CategoryName, PublicFilename


class ResourceRegistryPort(Protocol):
    """Read-only access to the active registry snapshot."""

    def list_resources(self, category: CategoryName) -> tuple[RegisteredResource, ...]:
        ...

    def get_resource(self, category: CategoryName, filename: PublicFilename) -> RegisteredResource:
        ...

    def category_exists(self, category: CategoryName) -> bool:
        ...
