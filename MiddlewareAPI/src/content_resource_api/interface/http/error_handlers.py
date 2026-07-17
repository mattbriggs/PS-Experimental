"""Map domain errors to HTTP responses."""

from fastapi import Request
from fastapi.responses import JSONResponse

from content_resource_api.domain.errors import (
    AuthenticationError,
    AuthorizationError,
    CategoryNotFound,
    ConflictingCredentials,
    ContentResourceError,
    InvalidResourceIdentifier,
    MissingCredential,
    ResourceNotRegistered,
    ResourceTooLarge,
    UpstreamError,
    UpstreamResourceMissing,
    UpstreamTimeout,
    UpstreamUnavailable,
)
from content_resource_api.interface.http.schemas import ErrorResponse


def _error_response(
    status: int, code: str, message: str, correlation_id: str | None = None
) -> JSONResponse:
    body = ErrorResponse(error_code=code, message=message, correlation_id=correlation_id)
    return JSONResponse(status_code=status, content=body.model_dump(exclude_none=True))


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", None)
    cid = str(correlation_id) if correlation_id else None

    if not isinstance(exc, ContentResourceError):
        return _error_response(500, "INTERNAL_ERROR", "An internal error occurred.", cid)
    if isinstance(exc, ConflictingCredentials):
        return _error_response(400, "CONFLICTING_CREDENTIALS", exc.safe_detail, cid)
    if isinstance(exc, MissingCredential):
        return _error_response(401, "MISSING_CREDENTIAL", exc.safe_detail, cid)
    if isinstance(exc, AuthenticationError):
        return _error_response(401, "AUTHENTICATION_FAILED", exc.safe_detail, cid)
    if isinstance(exc, AuthorizationError):
        return _error_response(403, "AUTHORIZATION_FAILED", exc.safe_detail, cid)
    if isinstance(exc, InvalidResourceIdentifier):
        return _error_response(400, "INVALID_IDENTIFIER", exc.safe_detail, cid)
    if isinstance(exc, (CategoryNotFound, ResourceNotRegistered)):
        return _error_response(404, "NOT_FOUND", "The requested resource was not found.", cid)
    if isinstance(exc, ResourceTooLarge):
        return _error_response(413, "RESOURCE_TOO_LARGE", exc.safe_detail, cid)
    if isinstance(exc, UpstreamResourceMissing):
        return _error_response(404, "NOT_FOUND", "The requested resource was not found.", cid)
    if isinstance(exc, UpstreamTimeout):
        return _error_response(503, "UPSTREAM_TIMEOUT", exc.safe_detail, cid)
    if isinstance(exc, UpstreamUnavailable):
        return _error_response(503, "UPSTREAM_UNAVAILABLE", exc.safe_detail, cid)
    if isinstance(exc, UpstreamError):
        return _error_response(502, "UPSTREAM_ERROR", exc.safe_detail, cid)
    return _error_response(500, "INTERNAL_ERROR", "An internal error occurred.", cid)
