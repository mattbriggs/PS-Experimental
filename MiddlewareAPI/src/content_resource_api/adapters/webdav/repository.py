"""WebDAV content repository adapter."""

import asyncio
import contextlib
from collections.abc import AsyncIterator
from datetime import UTC
from email.utils import parsedate_to_datetime

import httpx

from content_resource_api.adapters.webdav.mapping import map_httpx_error
from content_resource_api.domain.enums import DependencyState
from content_resource_api.domain.errors import UpstreamTransferError
from content_resource_api.domain.models import DependencyStatus, ResourceMetadata
from content_resource_api.domain.values import UpstreamResourceRef


class WebDavRepository:
    """Provides read-only access to WebDAV upstream objects."""

    def __init__(self, client: httpx.AsyncClient, max_concurrency: int = 20) -> None:
        self._client = client
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def get_metadata(self, resource_ref: UpstreamResourceRef) -> ResourceMetadata:
        async with self._semaphore:
            try:
                response = await self._client.head(str(resource_ref))
                response.raise_for_status()
            except Exception as exc:
                raise map_httpx_error(exc, safe_context="metadata retrieval") from exc

        etag = response.headers.get("ETag")
        last_modified = None
        lm_str = response.headers.get("Last-Modified")
        if lm_str:
            with contextlib.suppress(Exception):
                last_modified = parsedate_to_datetime(lm_str).replace(tzinfo=UTC)
        content_type = response.headers.get("Content-Type")
        content_length = None
        cl_str = response.headers.get("Content-Length")
        if cl_str and cl_str.isdigit():
            content_length = int(cl_str)

        return ResourceMetadata(
            etag=etag,
            last_modified=last_modified,
            content_type=content_type,
            content_length=content_length,
        )

    async def open_stream(
        self,
        resource_ref: UpstreamResourceRef,
        size_limit_bytes: int | None = None,
    ) -> AsyncIterator[bytes]:
        return self._stream(resource_ref, size_limit_bytes)

    async def _stream(
        self, resource_ref: UpstreamResourceRef, size_limit_bytes: int | None
    ) -> AsyncIterator[bytes]:
        async with self._semaphore:
            try:
                async with self._client.stream("GET", str(resource_ref)) as response:
                    response.raise_for_status()
                    total = 0
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        total += len(chunk)
                        if size_limit_bytes is not None and total > size_limit_bytes:
                            raise UpstreamTransferError(
                                "Resource exceeds size limit",
                                safe_detail="Resource too large",
                            )
                        yield chunk
            except UpstreamTransferError:
                raise
            except Exception as exc:
                raise map_httpx_error(exc, safe_context="content streaming") from exc

    async def check_availability(self) -> DependencyStatus:
        try:
            await self._client.head("/", timeout=5.0)
            return DependencyStatus(name="webdav", state=DependencyState.HEALTHY)
        except Exception:
            return DependencyStatus(
                name="webdav", state=DependencyState.UNAVAILABLE, detail="WebDAV unreachable"
            )
