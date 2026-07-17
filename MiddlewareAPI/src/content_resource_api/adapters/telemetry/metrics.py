"""Prometheus metrics adapter and NoOp fallback."""

import contextlib


class NoOpMetrics:
    def increment(self, name: str, labels: dict[str, str] | None = None) -> None:
        pass

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        pass


class PrometheusMetrics:
    """Real Prometheus metrics using prometheus_client."""

    def __init__(self) -> None:
        from prometheus_client import Counter, Histogram
        self._counters: dict[str, Counter] = {}
        self._histograms: dict[str, Histogram] = {}

        self.request_count = Counter(
            "content_resource_api_requests_total",
            "Total HTTP requests",
            ["method", "category", "status_code"],
        )
        self.request_duration = Histogram(
            "content_resource_api_request_duration_seconds",
            "HTTP request duration",
            ["method", "category"],
        )
        self.auth_failures_total = Counter(
            "content_resource_api_auth_failures_total",
            "Authentication failures",
            ["reason"],
        )
        self.upstream_errors_total = Counter(
            "content_resource_api_upstream_errors_total",
            "Upstream WebDAV errors",
            ["error_type"],
        )

    def increment(self, name: str, labels: dict[str, str] | None = None) -> None:
        with contextlib.suppress(Exception):
            if name == "auth_failure":
                reason = (labels or {}).get("reason", "unknown")
                self.auth_failures_total.labels(reason=reason).inc()
            elif name == "upstream_error":
                error_type = (labels or {}).get("error_type", "unknown")
                self.upstream_errors_total.labels(error_type=error_type).inc()

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        with contextlib.suppress(Exception):
            if name == "request_duration":
                method = (labels or {}).get("method", "unknown")
                category = (labels or {}).get("category", "unknown")
                self.request_duration.labels(method=method, category=category).observe(value)
