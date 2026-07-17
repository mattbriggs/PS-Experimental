"""Security tests for path traversal prevention."""

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


TRAVERSAL_PAYLOADS = [
    "../etc/passwd",
    "..%2Fetc%2Fpasswd",
    "..%252Fetc%252Fpasswd",
    "%2e%2e%2fetc%2fpasswd",
    "....//etc//passwd",
]


class TestTraversalPrevention:
    @pytest.mark.parametrize("payload", TRAVERSAL_PAYLOADS)
    def test_traversal_rejected_in_schematron(self, api_client, payload):
        r = api_client.get(
            f"/api/resources/v1/schematron/{payload}",
            headers={"X-API-Key": "test-client"},
        )
        assert r.status_code in (400, 404)

    @pytest.mark.parametrize("payload", TRAVERSAL_PAYLOADS)
    def test_traversal_rejected_in_taxonomy(self, api_client, payload):
        r = api_client.get(
            f"/api/resources/v1/taxonomy/{payload}",
            headers={"X-API-Key": "test-client"},
        )
        assert r.status_code in (400, 404)
