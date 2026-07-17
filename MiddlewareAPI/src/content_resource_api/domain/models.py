"""Immutable domain models.

All models are frozen Pydantic models. The byte stream itself is
represented as an AsyncIterator[bytes], not a Pydantic field.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from content_resource_api.domain.enums import AuditOutcome, DependencyState


class _FrozenModel(BaseModel):
    """Base for all immutable domain models."""

    model_config = ConfigDict(frozen=True)


class CorrelationId(_FrozenModel):
    """A validated request correlation identifier."""

    value: str = Field(min_length=1, max_length=128)

    @classmethod
    def generate(cls) -> CorrelationId:
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


class ResourceId(_FrozenModel):
    """A validated public resource identifier (category + filename)."""

    category: str
    filename: str


class ClientPrincipal(_FrozenModel):
    """An authenticated caller identity."""

    client_id: str
    scopes: frozenset[str]

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes


class CredentialInput(_FrozenModel):
    """Normalized credential extracted from request headers.

    Raw credential values are stored as plain strings here but must never
    be logged, serialized to responses, or included in error messages.
    """

    mechanism: str
    raw_value: str


class RegisteredResource(_FrozenModel):
    """A resource entry as resolved from the registry snapshot."""

    category: str
    public_filename: str
    upstream_object: str
    owner: str
    enabled: bool
    restricted: bool
    allowed_extensions: tuple[str, ...]
    size_limit_bytes: int
    required_scope: str


class ResourceMetadata(_FrozenModel):
    """Safe metadata retrieved from the upstream repository."""

    etag: str | None = None
    last_modified: datetime | None = None
    content_type: str | None = None
    content_length: int | None = None


class CacheDecision(_FrozenModel):
    """Result of conditional-request evaluation."""

    not_modified: bool
    etag: str | None = None
    last_modified: datetime | None = None


class AuthorizationDecision(_FrozenModel):
    """Result of an authorization policy check."""

    allowed: bool
    reason: str


class DependencyStatus(_FrozenModel):
    """Availability status of one external dependency."""

    name: str
    state: DependencyState
    detail: str | None = None


class HealthResult(_FrozenModel):
    """Health evaluation result."""

    live: bool
    ready: bool
    dependencies: tuple[DependencyStatus, ...] = Field(default_factory=tuple)


class AuditEventV1(_FrozenModel):
    """A versioned audit event record.

    Optional fields are omitted rather than serialized as null.
    """

    schema_version: str = "1"
    event_id: str
    correlation_id: str
    timestamp: datetime
    outcome: AuditOutcome
    category: str | None = None
    public_filename: str | None = None
    client_id: str | None = None
    scopes: tuple[str, ...] | None = None
    content_length: int | None = None
    upstream_latency_ms: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            k: v
            for k, v in self.model_dump().items()
            if v is not None
        }


class ErrorDetail(_FrozenModel):
    """A safe, schema-valid error response body."""

    error_code: str
    message: str
    correlation_id: str | None = None
