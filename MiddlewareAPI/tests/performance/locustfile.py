"""Locust load test file for the Content Resource API.

Usage (against a running instance):
    locust -f tests/performance/locustfile.py --host=http://localhost:8080

Environment variables:
    LOCUST_API_KEY  — API key to use for authenticated requests (required)
"""

import os

try:
    from locust import HttpUser, between, task
except ImportError:
    raise SystemExit("Install locust: pip install locust") from None

API_KEY = os.getenv("LOCUST_API_KEY", "dev-key-001")
AUTH = {"X-API-Key": API_KEY}
PREFIX = "/api/resources/v1"


class ContentResourceUser(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self):
        # Pre-fetch ETag for conditional request tests
        r = self.client.get(f"{PREFIX}/schematron/test-rules.sch", headers=AUTH)
        self.etag = r.headers.get("ETag", "")

    @task(3)
    def list_schematron(self):
        self.client.get(f"{PREFIX}/schematron", headers=AUTH, name="/schematron [list]")

    @task(5)
    def get_schematron_resource(self):
        self.client.get(
            f"{PREFIX}/schematron/test-rules.sch",
            headers=AUTH,
            name="/schematron/{filename} [retrieve]",
        )

    @task(4)
    def conditional_request(self):
        if self.etag:
            self.client.get(
                f"{PREFIX}/schematron/test-rules.sch",
                headers={**AUTH, "If-None-Match": self.etag},
                name="/schematron/{filename} [304]",
            )

    @task(2)
    def list_taxonomy(self):
        self.client.get(f"{PREFIX}/taxonomy", headers=AUTH, name="/taxonomy [list]")

    @task(1)
    def liveness(self):
        self.client.get(f"{PREFIX}/health/live", name="/health/live")

    @task(1)
    def invalid_resource(self):
        self.client.get(
            f"{PREFIX}/schematron/nonexistent.sch",
            headers=AUTH,
            name="/schematron/{filename} [404]",
        )
