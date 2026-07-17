"""Domain enumerations."""

from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DependencyState(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class AuditOutcome(StrEnum):
    SUCCESS = "success"
    NOT_MODIFIED = "not_modified"
    DENIED = "denied"
    FAILED = "failed"
    TRANSFER_FAILED = "transfer_failed"
