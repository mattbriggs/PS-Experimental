"""Domain error hierarchy.

All errors in this hierarchy must be safe to surface in log messages without
including WebDAV URLs, credentials, or upstream response bodies.
"""


class ContentResourceError(Exception):
    """Base error for all domain errors."""
    def __init__(self, message: str, safe_detail: str | None = None) -> None:
        super().__init__(message)
        self.safe_detail = safe_detail or message


class AuthenticationError(ContentResourceError):
    """Authentication could not be completed."""


class MissingCredential(AuthenticationError):
    """No credential was provided."""


class MalformedCredential(AuthenticationError):
    """The credential could not be parsed."""


class InvalidCredential(AuthenticationError):
    """The credential was syntactically valid but could not be verified."""


class ExpiredCredential(AuthenticationError):
    """The credential has expired."""


class RevokedCredential(AuthenticationError):
    """The credential has been revoked."""


class ConflictingCredentials(AuthenticationError):
    """Multiple incompatible credential mechanisms were presented."""


class AuthenticationServiceUnavailable(AuthenticationError):
    """The authentication backend is unavailable."""


class AuthorizationError(ContentResourceError):
    """The principal is not permitted to perform the requested operation."""


class InvalidResourceIdentifier(ContentResourceError):
    """The public resource identifier is syntactically invalid."""


class CategoryNotFound(ContentResourceError):
    """The requested category does not exist in the registry."""


class ResourceNotRegistered(ContentResourceError):
    """The requested resource is not registered or is disabled."""


class RegistryValidationError(ContentResourceError):
    """The registry configuration is invalid and cannot be activated."""


class UpstreamError(ContentResourceError):
    """An error occurred communicating with the upstream repository."""


class UpstreamResourceMissing(UpstreamError):
    """The registered object no longer exists upstream."""


class UpstreamTimeout(UpstreamError):
    """The upstream request exceeded the configured deadline."""


class UpstreamUnavailable(UpstreamError):
    """The upstream repository is temporarily unavailable."""


class UpstreamProtocolError(UpstreamError):
    """The upstream response could not be safely interpreted."""


class UpstreamTransferError(UpstreamError):
    """The upstream transfer was interrupted before completion."""


class ResourceTooLarge(ContentResourceError):
    """The resource exceeds the configured size limit."""


class AuditUnavailable(ContentResourceError):
    """The audit sink is unavailable."""


class InternalError(ContentResourceError):
    """An unexpected internal error occurred."""
