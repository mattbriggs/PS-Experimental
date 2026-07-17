"""Immutable registry snapshot backed by validated RegistryConfig."""

from content_resource_api.config.registry_models import CategoryEntry, RegistryConfig, ResourceEntry
from content_resource_api.domain.errors import CategoryNotFound, ResourceNotRegistered
from content_resource_api.domain.models import RegisteredResource
from content_resource_api.domain.values import CategoryName, PublicFilename


class RegistrySnapshot:
    """Thread-safe, immutable view of the validated registry."""

    def __init__(self, config: RegistryConfig) -> None:
        self._categories: dict[str, CategoryEntry] = {
            c.name: c for c in config.categories
        }
        self._resources: dict[tuple[str, str], ResourceEntry] = {}
        for cat in config.categories:
            for res in cat.resources:
                self._resources[(cat.name, res.public_filename)] = res

    def category_exists(self, category: CategoryName) -> bool:
        return str(category) in self._categories

    def list_resources(self, category: CategoryName) -> tuple[RegisteredResource, ...]:
        cat = self._categories.get(str(category))
        if cat is None or not cat.listing_enabled:
            raise CategoryNotFound(f"Category not found or not listable: {category!r}")
        return tuple(
            self._to_registered(cat, res)
            for res in sorted(cat.resources, key=lambda r: r.public_filename)
            if res.enabled
        )

    def get_resource(self, category: CategoryName, filename: PublicFilename) -> RegisteredResource:
        cat = self._categories.get(str(category))
        if cat is None:
            raise CategoryNotFound(f"Category not found: {category!r}")
        entry = self._resources.get((str(category), str(filename)))
        if entry is None or not entry.enabled:
            raise ResourceNotRegistered(f"Resource not registered: {filename!r} in {category!r}")
        return self._to_registered(cat, entry)

    @staticmethod
    def _to_registered(cat: CategoryEntry, res: ResourceEntry) -> RegisteredResource:
        scope = cat.allowed_scopes[0] if cat.allowed_scopes else ""
        return RegisteredResource(
            category=cat.name,
            public_filename=res.public_filename,
            upstream_object=res.upstream_object,
            owner=res.owner,
            enabled=res.enabled,
            restricted=res.restricted,
            allowed_extensions=tuple(cat.allowed_extensions),
            size_limit_bytes=cat.size_limit_bytes,
            required_scope=scope,
        )
