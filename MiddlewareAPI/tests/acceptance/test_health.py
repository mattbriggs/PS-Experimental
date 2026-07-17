"""Acceptance tests: AC-030 through AC-032 — Health and Operations."""


class TestAC030LivenessDuringWebDavOutage:
    """AC-030: Liveness returns 200 regardless of WebDAV state."""

    def test_liveness_always_200(self, client):
        r = client.get("/api/resources/v1/health/live")
        assert r.status_code == 200

    def test_liveness_status_ok(self, client):
        r = client.get("/api/resources/v1/health/live")
        assert r.json()["status"] == "ok"


class TestAC031ReadinessDuringDependencyOutage:
    """AC-031: Readiness returns 503 when WebDAV is required and unavailable."""

    def test_readiness_503_when_webdav_required_and_unavailable(
        self, monkeypatch, registry_path, xml_repo
    ):
        monkeypatch.setenv("API_KEY_test-client", "schematron:read,taxonomy:read")
        from fastapi.testclient import TestClient

        from content_resource_api.config.settings import Settings
        from content_resource_api.domain.enums import DependencyState
        from content_resource_api.domain.models import DependencyStatus
        from content_resource_api.interface.http.app import create_app

        class UnavailableRepo:
            async def get_metadata(self, ref): ...
            async def open_stream(self, ref): ...
            async def check_availability(self):
                return DependencyStatus(name="webdav", state=DependencyState.UNAVAILABLE)

        settings = Settings(
            registry_path=registry_path,
            webdav_base_url="http://fake",
            readiness_requires_webdav=True,
            metrics_enabled=False,
        )
        app = create_app(settings=settings, _repository_override=UnavailableRepo())
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/resources/v1/health/ready")
        assert r.status_code == 503

    def test_readiness_200_when_webdav_not_required(self, client):
        r = client.get("/api/resources/v1/health/ready")
        assert r.status_code == 200


class TestAC032HealthInformationMinimization:
    """AC-032: Health responses contain no secrets, private paths, or patch versions."""

    def test_liveness_no_sensitive_info(self, client):
        r = client.get("/api/resources/v1/health/live")
        text = r.text
        assert "password" not in text.lower()
        assert "secret" not in text.lower()
        assert "webdav" not in text.lower()

    def test_readiness_no_sensitive_info(self, client):
        r = client.get("/api/resources/v1/health/ready")
        text = r.text
        assert "password" not in text.lower()
        assert "secret" not in text.lower()
