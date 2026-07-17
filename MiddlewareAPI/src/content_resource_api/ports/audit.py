"""Audit sink port protocol."""

from typing import Protocol

from content_resource_api.domain.models import AuditEventV1


class AuditSinkPort(Protocol):
    async def emit(self, event: AuditEventV1) -> None:
        ...
