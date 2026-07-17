"""Shared fixtures for security tests."""

import shutil

import pytest
from fastapi.testclient import TestClient

from content_resource_api.config.settings import Settings
from content_resource_api.domain.models import ResourceMetadata
from content_resource_api.interface.http.app import create_app
from tests.doubles.content_repository import FakeContentRepository


@pytest.fixture
def registry_path(tmp_path):
    dest = tmp_path / "registry.yaml"
    shutil.copy("config/registry.test.yaml", dest)
    return str(dest)


@pytest.fixture
def xml_repo():
    return FakeContentRepository(
        metadata=ResourceMetadata(
            etag='"etag-abc"',
            content_type="application/xml",
            content_length=10,
        ),
        content=b"<rules/>",
    )


@pytest.fixture
def client(monkeypatch, registry_path, xml_repo):
    monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
    settings = Settings(
        registry_path=registry_path,
        webdav_base_url="http://fake",
        readiness_requires_webdav=False,
        metrics_enabled=False,
        auth_api_key_enabled=True,
    )
    app = create_app(settings=settings, _repository_override=xml_repo)
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-client"}
