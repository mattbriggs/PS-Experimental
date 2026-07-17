"""HTTP header extraction and correlation ID handling."""


from fastapi import Request

from content_resource_api.config.constants import (
    API_KEY_HEADER,
    CORRELATION_ID_HEADER,
    SAFE_CORRELATION_ID_CHARS,
)
from content_resource_api.domain.models import CorrelationId, CredentialInput


def extract_correlation_id(request: Request, max_length: int = 128) -> CorrelationId:
    raw = request.headers.get(CORRELATION_ID_HEADER)
    if raw and len(raw) <= max_length and all(c in SAFE_CORRELATION_ID_CHARS for c in raw):
        return CorrelationId(value=raw)
    return CorrelationId.generate()


def extract_api_key_credential(request: Request) -> CredentialInput | None:
    key = request.headers.get(API_KEY_HEADER)
    if key:
        return CredentialInput(mechanism="api_key", raw_value=key)
    return None


def extract_bearer_credential(request: Request) -> CredentialInput | None:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token:
            return CredentialInput(mechanism="bearer", raw_value=token)
    return None
