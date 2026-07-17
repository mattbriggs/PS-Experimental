"""Unit tests for authorization service."""

from content_resource_api.domain.authorization import AuthorizationService
from content_resource_api.domain.models import ClientPrincipal, RegisteredResource


def make_resource(scope="schematron:read", enabled=True, restricted=False):
    return RegisteredResource(
        category="schematron",
        public_filename="test.sch",
        upstream_object="schematron/test.sch",
        owner="test-team",
        enabled=enabled,
        restricted=restricted,
        allowed_extensions=(".sch",),
        size_limit_bytes=1048576,
        required_scope=scope,
    )


def make_principal(scopes: list[str]) -> ClientPrincipal:
    return ClientPrincipal(client_id="test", scopes=frozenset(scopes))


class TestAuthorizationService:
    def setup_method(self):
        self.service = AuthorizationService()

    def test_allows_with_correct_scope(self):
        principal = make_principal(["schematron:read"])
        resource = make_resource()
        result = self.service.authorize(principal, resource)
        assert result.allowed is True

    def test_denies_missing_scope(self):
        principal = make_principal(["taxonomy:read"])
        resource = make_resource()
        result = self.service.authorize(principal, resource)
        assert result.allowed is False

    def test_denies_disabled_resource(self):
        principal = make_principal(["schematron:read"])
        resource = make_resource(enabled=False)
        result = self.service.authorize(principal, resource)
        assert result.allowed is False
