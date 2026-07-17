"""Secret provider port."""

from typing import Protocol


class SecretProviderPort(Protocol):
    def get_secret(self, name: str) -> str | None:
        ...
