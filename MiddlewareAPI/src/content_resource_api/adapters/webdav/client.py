"""Shared async HTTPX client for WebDAV requests."""

import httpx

from content_resource_api.config.settings import Settings


def build_webdav_client(settings: Settings) -> httpx.AsyncClient:
    """Build a long-lived pooled HTTPX client for WebDAV access."""
    return httpx.AsyncClient(
        base_url=settings.webdav_base_url,
        auth=(settings.webdav_username, settings.webdav_password.get_secret_value()),
        timeout=httpx.Timeout(
            connect=settings.webdav_connect_timeout_seconds,
            read=settings.webdav_read_timeout_seconds,
            write=settings.webdav_connect_timeout_seconds,
            pool=settings.webdav_connect_timeout_seconds,
        ),
        limits=httpx.Limits(max_connections=settings.webdav_max_concurrency),
        headers={"User-Agent": "content-resource-api/1.0"},
    )
