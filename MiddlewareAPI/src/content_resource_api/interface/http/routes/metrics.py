"""Prometheus /metrics endpoint."""

from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(tags=["metrics"])


@router.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
