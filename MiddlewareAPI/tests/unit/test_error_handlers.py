"""Unit tests for HTTP error handler mapping."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from content_resource_api.domain.errors import (
    AuthorizationError,
    CategoryNotFound,
    ConflictingCredentials,
    InvalidCredential,
    InvalidResourceIdentifier,
    MissingCredential,
    ResourceNotRegistered,
    ResourceTooLarge,
    UpstreamProtocolError,
    UpstreamResourceMissing,
    UpstreamTimeout,
    UpstreamUnavailable,
)
from content_resource_api.interface.http.error_handlers import domain_error_handler


def make_test_app(exc_factory):
    app = FastAPI()
    from content_resource_api.domain.errors import ContentResourceError
    app.add_exception_handler(ContentResourceError, domain_error_handler)

    @app.get("/trigger")
    async def trigger():
        raise exc_factory()

    return TestClient(app, raise_server_exceptions=False)


class TestErrorHandlerMapping:
    def test_missing_credential_returns_401(self):
        client = make_test_app(lambda: MissingCredential("no cred"))
        r = client.get("/trigger")
        assert r.status_code == 401

    def test_invalid_credential_returns_401(self):
        client = make_test_app(lambda: InvalidCredential("bad cred", safe_detail="bad"))
        r = client.get("/trigger")
        assert r.status_code == 401

    def test_conflicting_credentials_returns_400(self):
        client = make_test_app(lambda: ConflictingCredentials("conflict"))
        r = client.get("/trigger")
        assert r.status_code == 400

    def test_authorization_error_returns_403(self):
        client = make_test_app(lambda: AuthorizationError("denied"))
        r = client.get("/trigger")
        assert r.status_code == 403

    def test_invalid_resource_identifier_returns_400(self):
        client = make_test_app(lambda: InvalidResourceIdentifier("bad id"))
        r = client.get("/trigger")
        assert r.status_code == 400

    def test_category_not_found_returns_404(self):
        client = make_test_app(lambda: CategoryNotFound("no cat"))
        r = client.get("/trigger")
        assert r.status_code == 404

    def test_resource_not_registered_returns_404(self):
        client = make_test_app(lambda: ResourceNotRegistered("no res"))
        r = client.get("/trigger")
        assert r.status_code == 404

    def test_upstream_resource_missing_returns_404(self):
        client = make_test_app(lambda: UpstreamResourceMissing("gone"))
        r = client.get("/trigger")
        assert r.status_code == 404

    def test_resource_too_large_returns_413(self):
        client = make_test_app(lambda: ResourceTooLarge("too big"))
        r = client.get("/trigger")
        assert r.status_code == 413

    def test_upstream_timeout_returns_503(self):
        client = make_test_app(lambda: UpstreamTimeout("timeout"))
        r = client.get("/trigger")
        assert r.status_code == 503

    def test_upstream_unavailable_returns_503(self):
        client = make_test_app(lambda: UpstreamUnavailable("down"))
        r = client.get("/trigger")
        assert r.status_code == 503

    def test_upstream_protocol_error_returns_502(self):
        client = make_test_app(lambda: UpstreamProtocolError("bad resp"))
        r = client.get("/trigger")
        assert r.status_code == 502

    def test_error_body_has_no_stack_trace(self):
        client = make_test_app(lambda: MissingCredential("no cred"))
        r = client.get("/trigger")
        text = r.text
        assert "Traceback" not in text
        assert "File " not in text
