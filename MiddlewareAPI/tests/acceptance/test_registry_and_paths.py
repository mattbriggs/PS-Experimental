"""Acceptance tests: AC-006 through AC-012 — Registry and Path Safety."""

import pytest


class TestAC006RegisteredResourceRetrieval:
    """AC-006: Registered resource resolves through registry, no upstream path in response."""

    def test_retrieval_returns_200(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron/test-rules.sch", headers=auth_headers)
        assert r.status_code == 200

    def test_response_does_not_disclose_upstream_path(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron/test-rules.sch", headers=auth_headers)
        assert "schematron/" not in r.headers.get("Content-Location", "")
        assert "webdav" not in r.text.lower()


class TestAC007UnknownResource:
    """AC-007: Unregistered filename returns 404, no upstream lookup."""

    def test_unregistered_filename_returns_404(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron/does-not-exist.sch", headers=auth_headers)
        assert r.status_code == 404

    def test_404_body_does_not_contain_upstream_path(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron/ghost.sch", headers=auth_headers)
        assert "schematron/" not in r.text


class TestAC008PlainTraversal:
    """AC-008: Plain traversal rejected, no WebDAV call."""

    def test_plain_traversal_rejected(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron/../etc/passwd", headers=auth_headers)
        assert r.status_code in (400, 404, 422)


class TestAC009EncodedTraversal:
    """AC-009: Encoded traversal sequences rejected."""

    @pytest.mark.parametrize("payload", [
        "%2e%2e%2frules.sch",
        "..%2Fetc%2Fpasswd",
        "%2F%2e%2e%2F",
    ])
    def test_encoded_traversal_rejected(self, client, auth_headers, payload):
        r = client.get(f"/api/resources/v1/schematron/{payload}", headers=auth_headers)
        assert r.status_code in (400, 404, 422)


class TestAC010DoubleEncodedTraversal:
    """AC-010: Double-encoded traversal rejected after bounded decoding."""

    @pytest.mark.parametrize("payload", [
        "..%252Fetc%252Fpasswd",
        "%252e%252e%252f",
    ])
    def test_double_encoded_traversal_rejected(self, client, auth_headers, payload):
        r = client.get(f"/api/resources/v1/schematron/{payload}", headers=auth_headers)
        assert r.status_code in (400, 404, 422)


class TestAC011UnsupportedExtension:
    """AC-011: Extension not approved for category is rejected."""

    def test_wrong_extension_rejected(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron/rules.exe", headers=auth_headers)
        assert r.status_code in (400, 404)


class TestAC012InvalidRegistryRoot:
    """AC-012: Invalid registry (escape from root) fails validation, readiness 503."""

    def test_invalid_registry_prevents_readiness(self, tmp_path, monkeypatch):
        import yaml
        bad_registry = {
            "schema_version": "1",
            "categories": [{
                "name": "schematron", "owner": "t",
                "listing_enabled": True,
                "allowed_scopes": ["s:read"],
                "allowed_extensions": [".sch"],
                "size_limit_bytes": 1000,
                "upstream_root": "s/",
                "resources": [
                    {"public_filename": "a.sch", "upstream_object": "/absolute/escape.sch",
                     "owner": "t", "enabled": True, "restricted": False},
                ],
            }],
        }
        path = tmp_path / "bad.yaml"
        path.write_text(yaml.dump(bad_registry))
        monkeypatch.setenv("API_KEY_x", "s:read")
        from content_resource_api.adapters.registry.yaml_loader import load_registry
        from content_resource_api.domain.errors import RegistryValidationError
        with pytest.raises(RegistryValidationError):
            load_registry(str(path))
