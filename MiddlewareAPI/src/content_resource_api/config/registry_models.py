"""Pydantic models for the resource registry configuration file."""

from pydantic import BaseModel, Field, field_validator, model_validator


class ResourceEntry(BaseModel):
    """A single registered resource within a category."""

    public_filename: str
    upstream_object: str
    owner: str
    enabled: bool = True
    restricted: bool = False

    @field_validator("upstream_object")
    @classmethod
    def must_be_relative(cls, v: str) -> str:
        if v.startswith("/") or v.startswith("\\"):
            raise ValueError("upstream_object must be a relative path, not absolute")
        return v


class CategoryEntry(BaseModel):
    """A resource category grouping registered resources."""

    name: str
    owner: str
    listing_enabled: bool = True
    allowed_scopes: list[str] = Field(min_length=1)
    allowed_extensions: list[str] = Field(min_length=1)
    size_limit_bytes: int = Field(gt=0)
    upstream_root: str
    resources: list[ResourceEntry] = Field(default_factory=list)

    @field_validator("upstream_root")
    @classmethod
    def root_must_be_relative(cls, v: str) -> str:
        if v.startswith("/") or v.startswith("\\"):
            raise ValueError("upstream_root must be a relative path")
        return v

    @model_validator(mode="after")
    def no_duplicate_filenames(self) -> "CategoryEntry":
        names = [r.public_filename for r in self.resources]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate public_filename in category '{self.name}'")
        return self

    @model_validator(mode="after")
    def resources_anchored_to_root(self) -> "CategoryEntry":
        for res in self.resources:
            if not res.upstream_object.startswith(self.upstream_root):
                raise ValueError(
                    f"upstream_object {res.upstream_object!r} does not start with "
                    f"upstream_root {self.upstream_root!r} in category {self.name!r}"
                )
        return self


class RegistryConfig(BaseModel):
    """Top-level registry configuration document."""

    schema_version: str
    categories: list[CategoryEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_schema_version(self) -> "RegistryConfig":
        if self.schema_version != "1":
            raise ValueError(f"Unsupported schema_version: {self.schema_version!r}")
        return self

    @model_validator(mode="after")
    def no_duplicate_categories(self) -> "RegistryConfig":
        names = [c.name for c in self.categories]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate category names in registry")
        return self
