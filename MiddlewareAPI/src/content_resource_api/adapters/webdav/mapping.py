"""Map WebDAV and network exceptions to domain errors."""

import httpx

from content_resource_api.domain.errors import (
    UpstreamProtocolError,
    UpstreamResourceMissing,
    UpstreamTimeout,
    UpstreamUnavailable,
)


def map_httpx_error(exc: Exception, safe_context: str = "upstream request") -> Exception:
    if isinstance(exc, httpx.TimeoutException):
        return UpstreamTimeout(
            f"Timeout during {safe_context}", safe_detail="Upstream request timed out"
        )
    if isinstance(exc, httpx.ConnectError):
        return UpstreamUnavailable(
            f"Connection failed during {safe_context}", safe_detail="Upstream unavailable"
        )
    if isinstance(exc, httpx.RemoteProtocolError):
        return UpstreamProtocolError(
            f"Protocol error during {safe_context}", safe_detail="Upstream protocol error"
        )
    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code == 404:
            return UpstreamResourceMissing(
                f"Object missing: {safe_context}", safe_detail="Resource not found upstream"
            )
        if exc.response.status_code in (503, 502):
            return UpstreamUnavailable(
                f"Upstream unavailable: {exc.response.status_code}",
                safe_detail="Upstream unavailable",
            )
        return UpstreamProtocolError(
            f"Unexpected status {exc.response.status_code}", safe_detail="Upstream error"
        )
    return UpstreamProtocolError(
        f"Unexpected upstream error: {type(exc).__name__}", safe_detail="Upstream error"
    )
