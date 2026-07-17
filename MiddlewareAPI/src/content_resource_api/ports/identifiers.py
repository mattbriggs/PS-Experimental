"""Identifier generator port."""

import uuid
from typing import Protocol


class IdentifierGeneratorPort(Protocol):
    def generate(self) -> str:
        ...


class UuidIdentifierGenerator:
    def generate(self) -> str:
        return str(uuid.uuid4())
