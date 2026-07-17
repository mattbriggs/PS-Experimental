"""Structured audit event sink — writes to the structured log."""

import structlog

from content_resource_api.domain.models import AuditEventV1

log = structlog.get_logger("audit")


class LoggingAuditSink:
    """Emit audit events as structured log entries."""

    async def emit(self, event: AuditEventV1) -> None:
        log.info("audit_event", **event.to_dict())
