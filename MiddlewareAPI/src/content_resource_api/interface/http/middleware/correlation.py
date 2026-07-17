"""Correlation ID middleware — attaches correlation ID to request state and response header."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from content_resource_api.config.constants import CORRELATION_ID_HEADER
from content_resource_api.interface.http.headers import extract_correlation_id


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_length: int = 128) -> None:
        super().__init__(app)
        self._max_length = max_length

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        cid = extract_correlation_id(request, max_length=self._max_length)
        request.state.correlation_id = cid
        response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER] = str(cid)
        return response
