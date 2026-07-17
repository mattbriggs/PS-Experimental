"""Test double for AuthenticationPort."""

from content_resource_api.domain.errors import InvalidCredential
from content_resource_api.domain.models import ClientPrincipal, CredentialInput


class FakeAuthenticationAdapter:
    def __init__(self, principals: dict[str, ClientPrincipal] | None = None) -> None:
        self._principals = principals or {}

    async def authenticate(self, credential: CredentialInput) -> ClientPrincipal:
        principal = self._principals.get(credential.raw_value)
        if principal is None:
            raise InvalidCredential("Invalid credential")
        return principal
