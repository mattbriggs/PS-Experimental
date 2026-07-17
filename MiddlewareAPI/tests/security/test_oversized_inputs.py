"""Security tests: oversized input handling."""


class TestOversizedInputs:
    def test_oversized_filename_rejected(self, client, auth_headers):
        long_name = "a" * 500 + ".sch"
        r = client.get(f"/api/resources/v1/schematron/{long_name}", headers=auth_headers)
        assert r.status_code in (400, 404, 422)

    def test_oversized_correlation_id_ignored(self, client, auth_headers):
        long_cid = "x" * 1000
        r = client.get(
            "/api/resources/v1/health/live",
            headers={"X-Correlation-ID": long_cid},
        )
        assert r.status_code == 200
        returned_cid = r.headers.get("X-Correlation-ID", "")
        assert returned_cid != long_cid  # replaced with generated UUID
