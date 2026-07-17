"""Acceptance tests: AC-022 through AC-025 — Conditional Requests."""


class TestAC022MatchingEtag:
    """AC-022: Matching If-None-Match returns 304 with no body."""

    def test_matching_etag_returns_304(self, client, auth_headers):
        r = client.get(
            "/api/resources/v1/schematron/test-rules.sch",
            headers={**auth_headers, "If-None-Match": '"etag-abc123"'},
        )
        assert r.status_code == 304

    def test_304_has_no_body(self, client, auth_headers):
        r = client.get(
            "/api/resources/v1/schematron/test-rules.sch",
            headers={**auth_headers, "If-None-Match": '"etag-abc123"'},
        )
        assert len(r.content) == 0


class TestAC023ChangedContent:
    """AC-023: Old ETag does not match when content has changed (different etag)."""

    def test_nonmatching_etag_returns_200(self, client, auth_headers):
        r = client.get(
            "/api/resources/v1/schematron/test-rules.sch",
            headers={**auth_headers, "If-None-Match": '"old-etag"'},
        )
        assert r.status_code == 200


class TestAC024ETagPrecedence:
    """AC-024: If-None-Match takes precedence over If-Modified-Since."""

    def test_nonmatching_etag_overrides_date(self, client, auth_headers):
        # ETag doesn't match (old), date would match (old enough) — ETag wins → 200
        r = client.get(
            "/api/resources/v1/schematron/test-rules.sch",
            headers={
                **auth_headers,
                "If-None-Match": '"nonmatching-etag"',
                "If-Modified-Since": "Wed, 01 Jan 2099 00:00:00 GMT",
            },
        )
        assert r.status_code == 200

    def test_matching_etag_overrides_date(self, client, auth_headers):
        # ETag matches, date old — ETag wins → 304
        r = client.get(
            "/api/resources/v1/schematron/test-rules.sch",
            headers={
                **auth_headers,
                "If-None-Match": '"etag-abc123"',
                "If-Modified-Since": "Wed, 01 Jan 2000 00:00:00 GMT",
            },
        )
        assert r.status_code == 304


class TestAC025LastModifiedValidation:
    """AC-025: If-Modified-Since evaluated when If-None-Match absent."""

    def test_future_date_returns_304(self, client, auth_headers):
        r = client.get(
            "/api/resources/v1/schematron/test-rules.sch",
            headers={**auth_headers, "If-Modified-Since": "Wed, 01 Jan 2099 00:00:00 GMT"},
        )
        assert r.status_code == 304

    def test_past_date_returns_200(self, client, auth_headers):
        r = client.get(
            "/api/resources/v1/schematron/test-rules.sch",
            headers={**auth_headers, "If-Modified-Since": "Wed, 01 Jan 2000 00:00:00 GMT"},
        )
        assert r.status_code == 200
