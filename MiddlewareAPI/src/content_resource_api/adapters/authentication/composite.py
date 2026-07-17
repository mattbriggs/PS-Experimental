"""Composite authentication adapter: selects mechanism and rejects conflicts."""

from content_resource_api.adapters.authentication.api_key import ApiKeyAuthenticationAdapter
from content_resource_api.domain.errors import ConflictingCredentials, MissingCredential
from content_resource_api.domain.models import ClientPrincipal, CredentialInput


class CompositeAuthenticationAdapter:
    """Selects and delegates to the configured authentication mechanism.

    Rejects requests that present multiple conflicting mechanisms.
    """

    def __init__(self, api_key_adapter: ApiKeyAuthenticationAdapter | None) -> None:
        self._api_key = api_key_adapter

    async def authenticate(
        self,
        api_key_credential: CredentialInput | None,
        bearer_credential: CredentialInput | None,
    ) -> ClientPrincipal:
        active = sum(1 for c in [api_key_credential, bearer_credential] if c is not None)
        if active > 1:
            raise ConflictingCredentials(
                "Multiple credential mechanisms presented",
                safe_detail="Only one authentication mechanism is permitted per request",
            )
        if active == 0:
            raise MissingCredential("No credential provided")

        credential = api_key_credential if api_key_credential is not None else bearer_credential
        if credential is None:
            raise MissingCredential("No credential provided")

        if credential.mechanism == "api_key" and self._api_key is not None:
            return await self._api_key.authenticate(credential)

        raise MissingCredential("No supported authentication mechanism matched")
