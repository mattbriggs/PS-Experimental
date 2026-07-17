"""Metrics port protocol."""

from typing import Protocol


class MetricsPort(Protocol):
    def increment(self, name: str, labels: dict[str, str] | None = None) -> None:
        ...

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        ...
