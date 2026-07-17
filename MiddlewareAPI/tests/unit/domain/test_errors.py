"""Unit tests for error hierarchy."""

from content_resource_api.domain.errors import (
    AuthenticationError,
    ContentResourceError,
    InvalidCredential,
    MissingCredential,
    UpstreamError,
    UpstreamTimeout,
)


class TestErrorHierarchy:
    def test_missing_credential_is_authentication_error(self):
        assert issubclass(MissingCredential, AuthenticationError)

    def test_invalid_credential_is_authentication_error(self):
        assert issubclass(InvalidCredential, AuthenticationError)

    def test_authentication_error_is_content_resource_error(self):
        assert issubclass(AuthenticationError, ContentResourceError)

    def test_upstream_timeout_is_upstream_error(self):
        assert issubclass(UpstreamTimeout, UpstreamError)

    def test_error_has_safe_detail(self):
        err = InvalidCredential("Internal reason", safe_detail="Authentication failed")
        assert err.safe_detail == "Authentication failed"
        assert "Internal reason" in str(err)
