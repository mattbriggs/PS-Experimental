"""Atomic registry snapshot reloader."""

import threading

from content_resource_api.adapters.registry.snapshot import RegistrySnapshot
from content_resource_api.adapters.registry.yaml_loader import load_registry
from content_resource_api.domain.errors import RegistryValidationError


class RegistrySnapshotManager:
    """Atomically replaces the active registry snapshot.

    The active snapshot is replaced only when validation succeeds.
    Concurrent reads always see a consistent, complete snapshot.
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._snapshot: RegistrySnapshot | None = None

    def load(self) -> None:
        config = load_registry(self._path)
        new_snapshot = RegistrySnapshot(config)
        with self._lock:
            self._snapshot = new_snapshot

    def reload(self) -> None:
        try:
            config = load_registry(self._path)
            new_snapshot = RegistrySnapshot(config)
        except RegistryValidationError:
            raise
        with self._lock:
            self._snapshot = new_snapshot

    @property
    def snapshot(self) -> RegistrySnapshot:
        with self._lock:
            if self._snapshot is None:
                raise RuntimeError("Registry not loaded; call load() first")
            return self._snapshot
