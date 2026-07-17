"""Public HTTP response schemas."""

from datetime import datetime

from pydantic import BaseModel


class ResourceItem(BaseModel):
    name: str
    path: str
    lastModified: datetime | None = None
    size: int | None = None
    contentType: str | None = None


class ResourceListResponse(BaseModel):
    resources: list[ResourceItem]


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    correlation_id: str | None = None


class HealthDependency(BaseModel):
    name: str
    state: str
    detail: str | None = None


class LivenessResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    dependencies: list[HealthDependency] = []
