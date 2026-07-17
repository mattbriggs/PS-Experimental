"""Health check routes."""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from content_resource_api.application.commands import EvaluateHealthQuery
from content_resource_api.domain.models import CorrelationId
from content_resource_api.interface.http.schemas import (
    HealthDependency,
    LivenessResponse,
    ReadinessResponse,
)

if TYPE_CHECKING:
    from content_resource_api.application.evaluate_health import EvaluateHealthHandler

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=LivenessResponse)
async def liveness() -> LivenessResponse:
    return LivenessResponse(status="ok")


@router.get("/ready", response_model=ReadinessResponse)
async def readiness(request: Request) -> JSONResponse:
    handler: EvaluateHealthHandler = request.app.state.health_handler
    result = await handler.handle(EvaluateHealthQuery(correlation_id=CorrelationId.generate()))
    status = "ok" if result.ready else "degraded"
    deps = [
        HealthDependency(name=d.name, state=d.state, detail=d.detail)
        for d in result.dependencies
    ]
    body = ReadinessResponse(status=status, dependencies=deps)
    http_status = 200 if result.ready else 503
    return JSONResponse(content=body.model_dump(exclude_none=True), status_code=http_status)
