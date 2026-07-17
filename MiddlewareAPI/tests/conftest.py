"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient

from content_resource_api.config.settings import Settings
from content_resource_api.interface.http.app import create_app


@pytest.fixture
def test_settings(tmp_path) -> Settings:
    import os
    import shutil
    registry_src = "config/registry.test.yaml"
    registry_dest = tmp_path / "registry.test.yaml"
    if os.path.exists(registry_src):
        shutil.copy(registry_src, registry_dest)
    else:
        with open("config/registry.test.yaml") as f:
            registry_dest.write_text(f.read())
    return Settings(
        registry_path=str(registry_dest),
        webdav_base_url="http://fake-webdav",
        webdav_username="test",
        webdav_password="test",
        auth_api_key_enabled=True,
        readiness_requires_webdav=False,
        audit_required=False,
        metrics_enabled=False,
    )


@pytest.fixture
def client(test_settings, monkeypatch) -> TestClient:
    monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
    monkeypatch.setenv("APP_REGISTRY_PATH", test_settings.registry_path)
    monkeypatch.setenv("APP_WEBDAV_BASE_URL", "http://fake-webdav")
    monkeypatch.setenv("APP_READINESS_REQUIRES_WEBDAV", "false")
    monkeypatch.setenv("APP_METRICS_ENABLED", "false")
    app = create_app(test_settings)
    return TestClient(app, raise_server_exceptions=False)
