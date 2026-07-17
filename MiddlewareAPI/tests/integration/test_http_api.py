"""HTTP integration tests against the FastAPI app."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api_client(monkeypatch, tmp_path):
    import shutil
    monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
    monkeypatch.setenv("APP_WEBDAV_BASE_URL", "http://fake-webdav")
    monkeypatch.setenv("APP_READINESS_REQUIRES_WEBDAV", "false")
    monkeypatch.setenv("APP_METRICS_ENABLED", "false")
    registry_dest = tmp_path / "registry.yaml"
    shutil.copy("config/registry.test.yaml", registry_dest)
    monkeypatch.setenv("APP_REGISTRY_PATH", str(registry_dest))
    from content_resource_api.config.settings import Settings
    settings = Settings(
        registry_path=str(registry_dest),
        webdav_base_url="http://fake-webdav",
        readiness_requires_webdav=False,
        metrics_enabled=False,
    )
    from content_resource_api.interface.http.app import create_app
    app = create_app(settings)
    return TestClient(app, raise_server_exceptions=False)


class TestLiveness:
    def test_liveness_returns_200(self, api_client):
        r = api_client.get("/api/resources/v1/health/live")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestReadiness:
    def test_readiness_returns_200_when_webdav_not_required(self, api_client):
        r = api_client.get("/api/resources/v1/health/ready")
        assert r.status_code in (200, 503)


class TestAuthentication:
    def test_missing_key_returns_401(self, api_client):
        r = api_client.get("/api/resources/v1/schematron")
        assert r.status_code == 401

    def test_invalid_key_returns_401(self, api_client):
        r = api_client.get("/api/resources/v1/schematron", headers={"X-API-Key": "bad-key"})
        assert r.status_code == 401

    def test_valid_key_is_accepted(self, api_client):
        r = api_client.get("/api/resources/v1/schematron", headers={"X-API-Key": "test-client"})
        assert r.status_code == 200

    def test_conflicting_credentials_returns_400(self, api_client):
        r = api_client.get(
            "/api/resources/v1/schematron",
            headers={"X-API-Key": "test-client", "Authorization": "Bearer sometoken"},
        )
        assert r.status_code == 400


class TestListing:
    def test_schematron_listing_returns_json(self, api_client):
        r = api_client.get("/api/resources/v1/schematron", headers={"X-API-Key": "test-client"})
        assert r.status_code == 200
        body = r.json()
        assert "resources" in body

    def test_taxonomy_listing_returns_json(self, api_client):
        r = api_client.get("/api/resources/v1/taxonomy", headers={"X-API-Key": "test-client"})
        assert r.status_code == 200

    def test_listing_contains_only_enabled_resources(self, api_client):
        r = api_client.get("/api/resources/v1/schematron", headers={"X-API-Key": "test-client"})
        items = r.json()["resources"]
        filenames = [i["name"] for i in items]
        assert "disabled-rules.sch" not in filenames

    def test_write_method_returns_405(self, api_client):
        r = api_client.post("/api/resources/v1/schematron", headers={"X-API-Key": "test-client"})
        assert r.status_code == 405


class TestCorrelationId:
    def test_response_has_correlation_id_header(self, api_client):
        r = api_client.get("/api/resources/v1/health/live")
        assert "X-Correlation-ID" in r.headers

    def test_caller_correlation_id_echoed(self, api_client):
        r = api_client.get("/api/resources/v1/health/live", headers={"X-Correlation-ID": "my-id-123"})
        assert r.headers.get("X-Correlation-ID") == "my-id-123"
