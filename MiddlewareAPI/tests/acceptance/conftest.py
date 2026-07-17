"""Shared fixtures for acceptance tests."""

import shutil
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from content_resource_api.config.settings import Settings
from content_resource_api.domain.models import ResourceMetadata
from content_resource_api.interface.http.app import create_app
from tests.doubles.content_repository import FakeContentRepository

XML_CONTENT = b'<?xml version="1.0" encoding="UTF-8"?><rules/>'
JSON_CONTENT = b'{"taxonomy": "test"}'

XML_METADATA = ResourceMetadata(
    etag='"etag-abc123"',
    last_modified=datetime(2024, 6, 1, tzinfo=UTC),
    content_type="application/xml",
    content_length=len(XML_CONTENT),
)

JSON_METADATA = ResourceMetadata(
    etag='"etag-json456"',
    last_modified=datetime(2024, 6, 1, tzinfo=UTC),
    content_type="application/json",
    content_length=len(JSON_CONTENT),
)


@pytest.fixture
def registry_path(tmp_path):
    src = "config/registry.test.yaml"
    dest = tmp_path / "registry.yaml"
    shutil.copy(src, dest)
    return str(dest)


@pytest.fixture
def xml_repo():
    return FakeContentRepository(metadata=XML_METADATA, content=XML_CONTENT)


@pytest.fixture
def json_repo():
    return FakeContentRepository(metadata=JSON_METADATA, content=JSON_CONTENT)


@pytest.fixture
def acceptance_app(monkeypatch, registry_path, xml_repo):
    monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
    settings = Settings(
        registry_path=registry_path,
        webdav_base_url="http://fake-webdav",
        readiness_requires_webdav=False,
        metrics_enabled=False,
        auth_api_key_enabled=True,
    )
    return create_app(settings=settings, _repository_override=xml_repo)


@pytest.fixture
def client(acceptance_app):
    return TestClient(acceptance_app, raise_server_exceptions=False)


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-client"}
