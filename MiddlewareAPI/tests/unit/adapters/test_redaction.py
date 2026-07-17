"""Unit tests for header redaction."""

from content_resource_api.adapters.telemetry.redaction import redact_headers


class TestRedactHeaders:
    def test_redacts_authorization(self):
        headers = {"Authorization": "Bearer secret-token", "Content-Type": "application/json"}
        result = redact_headers(headers)
        assert result["Authorization"] == "[REDACTED]"
        assert result["Content-Type"] == "application/json"

    def test_redacts_api_key(self):
        headers = {"X-API-Key": "my-secret-key"}
        result = redact_headers(headers)
        assert result["X-API-Key"] == "[REDACTED]"

    def test_redacts_cookie(self):
        headers = {"Cookie": "session=abc123"}
        result = redact_headers(headers)
        assert result["Cookie"] == "[REDACTED]"

    def test_case_insensitive(self):
        headers = {"authorization": "Basic xyz", "x-api-key": "key"}
        result = redact_headers(headers)
        assert result["authorization"] == "[REDACTED]"
        assert result["x-api-key"] == "[REDACTED]"

    def test_safe_headers_preserved(self):
        headers = {"Content-Length": "100", "X-Correlation-ID": "abc"}
        result = redact_headers(headers)
        assert result == headers
