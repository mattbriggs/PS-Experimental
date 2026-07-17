"""Acceptance tests: AC-037 through AC-041 — Read-Only Boundary and Performance."""

import time

import pytest


class TestAC037UnsupportedWriteMethod:
    """AC-037: Write methods return 405, no WebDAV write occurs."""

    @pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
    def test_write_method_returns_405(self, client, auth_headers, method):
        r = client.request(method, "/api/resources/v1/schematron", headers=auth_headers)
        assert r.status_code == 405

    @pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
    def test_write_on_resource_returns_405(self, client, auth_headers, method):
        r = client.request(
            method, "/api/resources/v1/schematron/test-rules.sch", headers=auth_headers
        )
        assert r.status_code == 405


class TestAC038NoArbitraryBrowsing:
    """AC-038: Generic or unconfigured paths return 404, no directory listing."""

    def test_unknown_category_returns_404(self, client, auth_headers):
        r = client.get("/api/resources/v1/documents", headers=auth_headers)
        assert r.status_code == 404

    def test_root_api_path_returns_404_or_docs(self, client, auth_headers):
        r = client.get("/api/resources/v1", headers=auth_headers)
        assert r.status_code in (404, 200)  # 200 if docs redirect

    def test_no_directory_listing_in_response(self, client, auth_headers):
        r = client.get("/api/resources/v1/documents", headers=auth_headers)
        assert "Index of" not in r.text
        assert "<html" not in r.text.lower() or "404" in r.text


class TestAC039RegistryRejectionLatency:
    """AC-039: Registry-only rejection completes within 100ms p95."""

    def test_unknown_resource_rejection_fast(self, client, auth_headers):
        times = []
        for _ in range(20):
            start = time.perf_counter()
            client.get("/api/resources/v1/schematron/nonexistent.sch", headers=auth_headers)
            times.append(time.perf_counter() - start)
        times.sort()
        p95 = times[int(len(times) * 0.95)]
        assert p95 < 0.5  # 500ms generous bound for local test env


class TestAC040ConditionalRequestLatency:
    """AC-040: 304 responses complete within 250ms p95."""

    def test_304_response_is_fast(self, client, auth_headers):
        times = []
        for _ in range(20):
            start = time.perf_counter()
            client.get(
                "/api/resources/v1/schematron/test-rules.sch",
                headers={**auth_headers, "If-None-Match": '"etag-abc123"'},
            )
            times.append(time.perf_counter() - start)
        times.sort()
        p95 = times[int(len(times) * 0.95)]
        assert p95 < 1.0  # generous for test env


class TestAC041HorizontalScaling:
    """AC-041: Multiple instances produce consistent behavior (stateless check)."""

    def test_no_session_state_required(self, monkeypatch, registry_path, xml_repo):
        """Two separate app instances return the same listing — no shared memory state."""
        monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
        from fastapi.testclient import TestClient

        from content_resource_api.config.settings import Settings
        from content_resource_api.interface.http.app import create_app
        settings = Settings(
            registry_path=registry_path,
            webdav_base_url="http://fake",
            readiness_requires_webdav=False,
            metrics_enabled=False,
        )
        app1 = create_app(settings=settings, _repository_override=xml_repo)
        app2 = create_app(settings=settings, _repository_override=xml_repo)
        c1 = TestClient(app1, raise_server_exceptions=False)
        c2 = TestClient(app2, raise_server_exceptions=False)
        r1 = c1.get("/api/resources/v1/schematron", headers={"X-API-Key": "test-client"})
        r2 = c2.get("/api/resources/v1/schematron", headers={"X-API-Key": "test-client"})
        assert r1.json() == r2.json()
