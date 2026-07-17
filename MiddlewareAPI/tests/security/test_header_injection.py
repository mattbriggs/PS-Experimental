"""Security tests: header injection prevention."""



class TestHeaderInjection:
    def test_newline_in_correlation_id_sanitized(self, client, auth_headers):
        """Newline characters in correlation ID are rejected/replaced."""
        r = client.get(
            "/api/resources/v1/health/live",
            headers={"X-Correlation-ID": "id\r\nX-Injected: evil"},
        )
        injected = r.headers.get("X-Injected")
        assert injected is None

    def test_null_byte_in_filename_rejected(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron/file%00.sch", headers=auth_headers)
        assert r.status_code in (400, 404, 422)

    def test_long_api_key_handled_safely(self, client):
        long_key = "A" * 10000
        r = client.get("/api/resources/v1/schematron", headers={"X-API-Key": long_key})
        assert r.status_code == 401
        assert long_key not in r.text
