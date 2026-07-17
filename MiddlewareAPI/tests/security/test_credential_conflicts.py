"""Security tests: credential conflict handling."""


class TestCredentialConflicts:
    def test_api_key_and_bearer_rejected(self, client):
        r = client.get(
            "/api/resources/v1/schematron",
            headers={"X-API-Key": "test-client", "Authorization": "Bearer token"},
        )
        assert r.status_code == 400

    def test_conflict_error_does_not_leak_credentials(self, client):
        r = client.get(
            "/api/resources/v1/schematron",
            headers={"X-API-Key": "secret-key-value", "Authorization": "Bearer other-secret"},
        )
        assert "secret-key-value" not in r.text
        assert "other-secret" not in r.text
