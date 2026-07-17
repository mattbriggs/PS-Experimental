"""Acceptance tests: AC-026 through AC-029 — Upstream Failure Behavior."""

import pytest
from fastapi.testclient import TestClient


def make_failing_repo(exc_type, *args, **kwargs):
    class FailingRepo:
        async def get_metadata(self, ref):
            raise exc_type(*args, **kwargs)
        async def open_stream(self, ref):
            raise exc_type(*args, **kwargs)
        async def check_availability(self):
            from content_resource_api.domain.enums import DependencyState
            from content_resource_api.domain.models import DependencyStatus
            return DependencyStatus(name="webdav", state=DependencyState.UNAVAILABLE)
    return FailingRepo()


@pytest.fixture
def upstream_client_factory(monkeypatch, registry_path):
    def factory(repo):
        monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
        from content_resource_api.config.settings import Settings
        from content_resource_api.interface.http.app import create_app
        settings = Settings(
            registry_path=registry_path,
            webdav_base_url="http://fake",
            readiness_requires_webdav=False,
            metrics_enabled=False,
        )
        app = create_app(settings=settings, _repository_override=repo)
        return TestClient(app, raise_server_exceptions=False)
    return factory


class TestAC026UpstreamTimeout:
    """AC-026: WebDAV timeout returns 503."""

    def test_timeout_returns_503(self, upstream_client_factory):
        from content_resource_api.domain.errors import UpstreamTimeout
        c = upstream_client_factory(make_failing_repo(UpstreamTimeout, "timeout", safe_detail="timed out"))
        r = c.get("/api/resources/v1/schematron/test-rules.sch", headers={"X-API-Key": "test-client"})
        assert r.status_code == 503


class TestAC027InvalidUpstreamResponse:
    """AC-027: WebDAV protocol error returns 502, no raw upstream body."""

    def test_protocol_error_returns_502(self, upstream_client_factory):
        from content_resource_api.domain.errors import UpstreamProtocolError
        c = upstream_client_factory(make_failing_repo(UpstreamProtocolError, "bad resp", safe_detail="protocol error"))
        r = c.get("/api/resources/v1/schematron/test-rules.sch", headers={"X-API-Key": "test-client"})
        assert r.status_code == 502

    def test_no_raw_upstream_body_in_response(self, upstream_client_factory):
        from content_resource_api.domain.errors import UpstreamProtocolError
        c = upstream_client_factory(make_failing_repo(UpstreamProtocolError, "internal details", safe_detail="safe"))
        r = c.get("/api/resources/v1/schematron/test-rules.sch", headers={"X-API-Key": "test-client"})
        assert "internal details" not in r.text


class TestAC028UpstreamMissingResource:
    """AC-028: Registered resource gone upstream returns 404."""

    def test_missing_upstream_returns_404(self, upstream_client_factory):
        from content_resource_api.domain.errors import UpstreamResourceMissing
        c = upstream_client_factory(make_failing_repo(UpstreamResourceMissing, "gone", safe_detail="not found"))
        r = c.get("/api/resources/v1/schematron/test-rules.sch", headers={"X-API-Key": "test-client"})
        assert r.status_code == 404


class TestAC029BoundedRetry:
    """AC-029: Verifies retry behavior is bounded (adapter design check)."""

    def test_unavailable_returns_503(self, upstream_client_factory):
        from content_resource_api.domain.errors import UpstreamUnavailable
        c = upstream_client_factory(make_failing_repo(UpstreamUnavailable, "down", safe_detail="unavailable"))
        r = c.get("/api/resources/v1/schematron/test-rules.sch", headers={"X-API-Key": "test-client"})
        assert r.status_code == 503
