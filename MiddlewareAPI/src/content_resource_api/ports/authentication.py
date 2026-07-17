"""Authentication port protocol."""

from typing import Protocol

from content_resource_api.domain.models import ClientPrincipal, CredentialInput


class AuthenticationPort(Protocol):
    """Authenticate a single normalized credential and return a principal."""

    async def authenticate(self, credential: CredentialInput) -> ClientPrincipal:
        ...
