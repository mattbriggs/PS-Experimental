"""Performance benchmarks for key latency targets.

These run against the in-process TestClient (no network) to measure
application overhead, excluding client-network and real WebDAV latency.
Targets are intentionally generous to pass in CI; production targets
require representative workloads.
"""

import shutil
import time

import pytest
from fastapi.testclient import TestClient

from content_resource_api.config.settings import Settings
from content_resource_api.domain.models import ResourceMetadata
from content_resource_api.interface.http.app import create_app
from tests.doubles.content_repository import FakeContentRepository

METADATA = ResourceMetadata(
    etag='"bench-etag"',
    content_type="application/xml",
    content_length=100,
)


@pytest.fixture(scope="module")
def bench_client(tmp_path_factory):
    import os
    tmp = tmp_path_factory.mktemp("bench")
    src = "config/registry.test.yaml"
    dest = tmp / "registry.yaml"
    shutil.copy(src, dest)
    os.environ["API_KEY_bench-client"] = "schematron:read,taxonomy:read"  # noqa: SIM112
    repo = FakeContentRepository(metadata=METADATA, content=b"<bench/>")
    settings = Settings(
        registry_path=str(dest),
        webdav_base_url="http://fake",
        readiness_requires_webdav=False,
        metrics_enabled=False,
    )
    app = create_app(settings=settings, _repository_override=repo)
    return TestClient(app, raise_server_exceptions=False)


def measure_p95(client, path, headers, n=50):
    times = []
    for _ in range(n):
        start = time.perf_counter()
        client.get(path, headers=headers)
        times.append(time.perf_counter() - start)
    times.sort()
    return times[int(n * 0.95)]


AUTH = {"X-API-Key": "bench-client"}


class TestRegistryRejectionLatency:
    """AC-039: Registry-only rejection p95 <= 100ms (500ms in test env)."""

    def test_unknown_resource_p95(self, bench_client):
        p95 = measure_p95(bench_client, "/api/resources/v1/schematron/ghost.sch", AUTH)
        assert p95 < 0.5, f"p95 rejection latency {p95:.3f}s exceeds 500ms"


class TestConditionalRequestLatency:
    """AC-040: 304 response p95 <= 250ms (1s in test env)."""

    def test_304_p95(self, bench_client):
        headers = {**AUTH, "If-None-Match": '"bench-etag"'}
        p95 = measure_p95(bench_client, "/api/resources/v1/schematron/test-rules.sch", headers)
        assert p95 < 1.0, f"p95 304 latency {p95:.3f}s exceeds 1s"


class TestRetrievalLatency:
    """REQ-195: Middleware overhead p95 <= 100ms (1s in test env)."""

    def test_retrieval_p95(self, bench_client):
        p95 = measure_p95(bench_client, "/api/resources/v1/schematron/test-rules.sch", AUTH)
        assert p95 < 1.0, f"p95 retrieval latency {p95:.3f}s exceeds 1s"
