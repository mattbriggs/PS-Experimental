"""Security tests: credential redaction in outputs."""


class TestLogRedaction:
    def test_api_key_absent_from_error_body(self, client):
        secret = "VERY-SECRET-API-KEY-DO-NOT-LEAK"
        r = client.get("/api/resources/v1/schematron", headers={"X-API-Key": secret})
        assert secret not in r.text
        assert secret not in r.headers.get("X-Correlation-ID", "")

    def test_bearer_token_absent_from_error_body(self, client):
        token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.secret-payload"
        r = client.get("/api/resources/v1/schematron", headers={"Authorization": f"Bearer {token}"})
        assert token not in r.text

    def test_upstream_details_absent_from_502(self, monkeypatch, registry_path, xml_repo):
        monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
        from content_resource_api.domain.errors import UpstreamProtocolError

        class LeakyRepo:
            async def get_metadata(self, ref):
                raise UpstreamProtocolError(
                    "INTERNAL: http://internal-webdav:8080/private-path/secret",
                    safe_detail="upstream error",
                )
            async def open_stream(self, ref): ...
            async def check_availability(self): ...

        from fastapi.testclient import TestClient

        from content_resource_api.config.settings import Settings
        from content_resource_api.interface.http.app import create_app
        settings = Settings(
            registry_path=registry_path,
            webdav_base_url="http://fake",
            readiness_requires_webdav=False,
            metrics_enabled=False,
        )
        app = create_app(settings=settings, _repository_override=LeakyRepo())
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/resources/v1/schematron/test-rules.sch", headers={"X-API-Key": "test-client"})
        assert "internal-webdav" not in r.text
        assert "private-path" not in r.text
        assert "secret" not in r.text
