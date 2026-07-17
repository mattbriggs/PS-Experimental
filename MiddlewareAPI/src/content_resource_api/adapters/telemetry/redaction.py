"""Sensitive-value redaction utilities."""

import re

_REDACTED = "[REDACTED]"
_AUTH_HEADER = re.compile(r"(Authorization:\s*\S+\s+)\S+", re.IGNORECASE)
_API_KEY_HEADER = re.compile(r"(X-API-Key:\s*)\S+", re.IGNORECASE)


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    sensitive = {"authorization", "x-api-key", "cookie", "set-cookie"}
    return {
        k: (_REDACTED if k.lower() in sensitive else v)
        for k, v in headers.items()
    }
