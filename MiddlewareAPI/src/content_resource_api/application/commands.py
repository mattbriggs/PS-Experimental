"""Command and query objects for application use cases."""

from datetime import datetime

from pydantic import BaseModel

from content_resource_api.domain.models import CorrelationId


class ListResourcesCommand(BaseModel):
    """Command to list resources in a category."""
    model_config = {"frozen": True}
    category: str
    correlation_id: CorrelationId
    principal_id: str
    principal_scopes: frozenset[str]


class GetResourceCommand(BaseModel):
    """Command to retrieve a resource."""
    model_config = {"frozen": True}
    category: str
    filename: str
    correlation_id: CorrelationId
    principal_id: str
    principal_scopes: frozenset[str]
    if_none_match: str | None = None
    if_modified_since: datetime | None = None


class EvaluateHealthQuery(BaseModel):
    model_config = {"frozen": True}
    correlation_id: CorrelationId
