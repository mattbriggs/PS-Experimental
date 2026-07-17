"""Acceptance tests: AC-017 through AC-021 — Retrieval and Content Integrity."""

from fastapi.testclient import TestClient


class TestAC017RawXmlRetrieval:
    """AC-017: XML resource bytes match upstream, content-type is application/xml."""

    def test_xml_resource_returns_200(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron/test-rules.sch", headers=auth_headers)
        assert r.status_code == 200

    def test_xml_content_type(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron/test-rules.sch", headers=auth_headers)
        assert "application/xml" in r.headers.get("content-type", "")

    def test_raw_bytes_returned(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron/test-rules.sch", headers=auth_headers)
        assert b"<rules/>" in r.content


class TestAC018JsonContentType:
    """AC-018: .json taxonomy resource returns application/json."""

    def test_json_resource_content_type(self, monkeypatch, registry_path, json_repo):
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
        app = create_app(settings=settings, _repository_override=json_repo)
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/resources/v1/taxonomy/test-taxonomy.json", headers={"X-API-Key": "test-client"})
        assert r.status_code == 200
        assert "json" in r.headers.get("content-type", "")


class TestAC020OversizedResource:
    """AC-020: Resource exceeding size limit returns 413, never 200."""

    def test_oversized_does_not_return_200(self, monkeypatch, registry_path):
        from content_resource_api.domain.models import ResourceMetadata
        monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")

        class OversizedRepo:
            async def get_metadata(self, ref):
                # content_length > registry size_limit_bytes (1 MiB = 1_048_576)
                return ResourceMetadata(content_type="application/xml", content_length=10_000_000)

            async def open_stream(self, ref):
                async def gen():
                    yield b"data"
                return gen()

            async def check_availability(self):
                from content_resource_api.domain.enums import DependencyState
                from content_resource_api.domain.models import DependencyStatus
                return DependencyStatus(name="webdav", state=DependencyState.HEALTHY)

        from fastapi.testclient import TestClient

        from content_resource_api.config.settings import Settings
        from content_resource_api.interface.http.app import create_app
        settings = Settings(
            registry_path=registry_path,
            webdav_base_url="http://fake",
            readiness_requires_webdav=False,
            metrics_enabled=False,
        )
        app = create_app(settings=settings, _repository_override=OversizedRepo())
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/resources/v1/schematron/test-rules.sch", headers={"X-API-Key": "test-client"})
        assert r.status_code == 413


class TestTaxonomyRetrieval:
    """Taxonomy category GET /{filename} — exercises taxonomy route handler."""

    def test_taxonomy_retrieval_returns_200(self, monkeypatch, registry_path, json_repo):
        monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
        from content_resource_api.config.settings import Settings
        from content_resource_api.interface.http.app import create_app
        settings = Settings(
            registry_path=registry_path,
            webdav_base_url="http://fake",
            readiness_requires_webdav=False,
            metrics_enabled=False,
        )
        app = create_app(settings=settings, _repository_override=json_repo)
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/resources/v1/taxonomy/test-taxonomy.json", headers={"X-API-Key": "test-client"})
        assert r.status_code == 200
        assert b"taxonomy" in r.content

    def test_taxonomy_conditional_request_304(self, monkeypatch, registry_path, json_repo):
        monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
        from content_resource_api.config.settings import Settings
        from content_resource_api.interface.http.app import create_app
        settings = Settings(
            registry_path=registry_path,
            webdav_base_url="http://fake",
            readiness_requires_webdav=False,
            metrics_enabled=False,
        )
        app = create_app(settings=settings, _repository_override=json_repo)
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get(
            "/api/resources/v1/taxonomy/test-taxonomy.json",
            headers={"X-API-Key": "test-client", "If-None-Match": '"etag-json456"'},
        )
        assert r.status_code == 304

    def test_taxonomy_unregistered_returns_404(self, client, auth_headers):
        r = client.get("/api/resources/v1/taxonomy/ghost.json", headers=auth_headers)
        assert r.status_code == 404

    def test_taxonomy_traversal_rejected(self, client, auth_headers):
        r = client.get("/api/resources/v1/taxonomy/..%2Fetc", headers=auth_headers)
        assert r.status_code in (400, 404, 422)

    def test_taxonomy_if_modified_since_past_returns_200(self, monkeypatch, registry_path, json_repo):
        monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
        from content_resource_api.config.settings import Settings
        from content_resource_api.interface.http.app import create_app
        settings = Settings(
            registry_path=registry_path,
            webdav_base_url="http://fake",
            readiness_requires_webdav=False,
            metrics_enabled=False,
        )
        app = create_app(settings=settings, _repository_override=json_repo)
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get(
            "/api/resources/v1/taxonomy/test-taxonomy.json",
            headers={"X-API-Key": "test-client", "If-Modified-Since": "Wed, 01 Jan 2000 00:00:00 GMT"},
        )
        assert r.status_code == 200
