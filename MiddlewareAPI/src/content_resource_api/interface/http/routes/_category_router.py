"""Shared factory for category resource routes (listing + retrieval)."""

import contextlib
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import Response, StreamingResponse

from content_resource_api.application.commands import GetResourceCommand, ListResourcesCommand
from content_resource_api.application.results import NotModifiedResult
from content_resource_api.domain.validators import validate_public_filename
from content_resource_api.interface.http.dependencies import CorrelationIdDep, PrincipalDep
from content_resource_api.interface.http.schemas import ResourceItem, ResourceListResponse

if TYPE_CHECKING:
    from content_resource_api.application.get_resource import GetResourceHandler
    from content_resource_api.application.list_resources import ListResourcesHandler


def make_category_router(category: str, prefix: str, tags: list[str]) -> APIRouter:
    """Build a standard resource listing + retrieval router for a category."""
    router = APIRouter(prefix=prefix, tags=tags)  # type: ignore[arg-type]

    @router.get("", response_model=ResourceListResponse)
    async def list_resources(
        request: Request,
        correlation_id: CorrelationIdDep,
        principal: PrincipalDep,
    ) -> ResourceListResponse:
        handler: ListResourcesHandler = request.app.state.list_handler
        result = handler.handle(ListResourcesCommand(
            category=category,
            correlation_id=correlation_id,
            principal_id=principal.client_id,
            principal_scopes=principal.scopes,
        ))
        return ResourceListResponse(
            resources=[ResourceItem(**i.model_dump()) for i in result.items]
        )

    @router.get("/{filename}")
    async def get_resource(
        filename: str,
        request: Request,
        correlation_id: CorrelationIdDep,
        principal: PrincipalDep,
    ) -> Response:
        settings_obj = getattr(request.app.state, "settings", None)
        max_len = settings_obj.filename_max_length if settings_obj else 200
        validate_public_filename(filename, max_length=max_len)

        handler: GetResourceHandler = request.app.state.get_handler
        if_none_match = request.headers.get("If-None-Match")
        if_modified_since = None
        ims_str = request.headers.get("If-Modified-Since")
        if ims_str:
            with contextlib.suppress(Exception):
                if_modified_since = parsedate_to_datetime(ims_str)

        result = await handler.handle(GetResourceCommand(
            category=category,
            filename=filename,
            correlation_id=correlation_id,
            principal_id=principal.client_id,
            principal_scopes=principal.scopes,
            if_none_match=if_none_match,
            if_modified_since=if_modified_since,
        ))
        if isinstance(result, NotModifiedResult):
            headers: dict[str, str] = {}
            if result.etag:
                headers["ETag"] = result.etag
            return Response(status_code=304, headers=headers)
        headers = {}
        if result.metadata.etag:
            headers["ETag"] = result.metadata.etag
        if result.metadata.content_type:
            headers["Content-Type"] = result.metadata.content_type
        if result.metadata.content_length is not None:
            headers["Content-Length"] = str(result.metadata.content_length)
        return StreamingResponse(
            result.stream,
            status_code=200,
            headers=headers,
            media_type=result.metadata.content_type,
        )

    return router
