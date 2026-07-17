"""API-key authentication adapter.

API keys are loaded from environment variables in the format:
  API_KEY_<client-id>=scope1:read,scope2:read

Credentials are never logged or included in error messages.
"""

import os
import re

from content_resource_api.domain.errors import InvalidCredential, MissingCredential
from content_resource_api.domain.models import ClientPrincipal, CredentialInput

_ENV_PREFIX = "API_KEY_"
_KEY_ID_PATTERN = re.compile(r"^[A-Za-z0-9_\-]+$")


def _load_api_keys() -> dict[str, frozenset[str]]:
    keys: dict[str, frozenset[str]] = {}
    for var, value in os.environ.items():
        if var.startswith(_ENV_PREFIX):
            client_id = var[len(_ENV_PREFIX):]
            scopes = frozenset(s.strip() for s in value.split(",") if s.strip())
            keys[client_id] = scopes
    return keys


class ApiKeyAuthenticationAdapter:
    """Authenticates requests using X-API-Key header values."""

    def __init__(self) -> None:
        self._keys = _load_api_keys()

    async def authenticate(self, credential: CredentialInput) -> ClientPrincipal:
        if credential.mechanism != "api_key":
            raise MissingCredential("No API key credential provided")

        raw = credential.raw_value
        for client_id, scopes in self._keys.items():
            if raw == client_id:
                return ClientPrincipal(client_id=client_id, scopes=scopes)

        raise InvalidCredential("Invalid API key", safe_detail="Authentication failed")
