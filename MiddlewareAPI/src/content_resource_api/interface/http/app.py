"""FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from content_resource_api.adapters.authentication.api_key import ApiKeyAuthenticationAdapter
from content_resource_api.adapters.authentication.composite import CompositeAuthenticationAdapter
from content_resource_api.adapters.registry.reloader import RegistrySnapshotManager
from content_resource_api.adapters.telemetry.logging import configure_logging
from content_resource_api.adapters.webdav.client import build_webdav_client
from content_resource_api.adapters.webdav.repository import WebDavRepository
from content_resource_api.application.evaluate_health import EvaluateHealthHandler
from content_resource_api.application.get_resource import GetResourceHandler
from content_resource_api.application.list_resources import ListResourcesHandler
from content_resource_api.config.constants import API_PREFIX
from content_resource_api.config.settings import Settings
from content_resource_api.domain.authorization import AuthorizationService
from content_resource_api.domain.conditional_requests import ConditionalRequestService
from content_resource_api.domain.errors import ContentResourceError
from content_resource_api.interface.http.error_handlers import domain_error_handler
from content_resource_api.interface.http.middleware.correlation import CorrelationIdMiddleware
from content_resource_api.interface.http.routes import health, metrics, schematron, taxonomy


def create_app(
    settings: Settings | None = None,
    _repository_override: Any | None = None,
) -> FastAPI:
    """Create the FastAPI application.

    :param settings: Optional settings; loaded from environment when omitted.
    :param _repository_override: Inject a test double for the content repository.
        This parameter is for testing only and must not be used in production.
    """
    if settings is None:
        settings = Settings()

    configure_logging(settings.app_log_level)

    registry_manager = RegistrySnapshotManager(settings.registry_path)
    registry_manager.load()

    if _repository_override is not None:
        repository = _repository_override
        webdav_client = None
    else:
        webdav_client = build_webdav_client(settings)
        repository = WebDavRepository(webdav_client, settings.webdav_max_concurrency)

    api_key_adapter = ApiKeyAuthenticationAdapter() if settings.auth_api_key_enabled else None
    auth_adapter = CompositeAuthenticationAdapter(api_key_adapter=api_key_adapter)

    auth_service = AuthorizationService()
    cond_service = ConditionalRequestService()

    list_handler = ListResourcesHandler(
        registry=registry_manager.snapshot,
        auth_service=auth_service,
    )
    get_handler = GetResourceHandler(
        registry=registry_manager.snapshot,
        repository=repository,
        auth_service=auth_service,
        cond_service=cond_service,
    )
    health_handler = EvaluateHealthHandler(
        repository=repository,
        readiness_requires_webdav=settings.readiness_requires_webdav,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        yield
        if webdav_client is not None:
            await webdav_client.aclose()

    app = FastAPI(
        title="Content Resource API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.state.settings = settings
    app.state.registry_manager = registry_manager
    app.state.auth_adapter = auth_adapter
    app.state.list_handler = list_handler
    app.state.get_handler = get_handler
    app.state.health_handler = health_handler

    app.add_middleware(CorrelationIdMiddleware, max_length=settings.correlation_id_max_length)
    app.add_exception_handler(ContentResourceError, domain_error_handler)

    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(schematron.router, prefix=API_PREFIX)
    app.include_router(taxonomy.router, prefix=API_PREFIX)
    app.include_router(metrics.router)

    return app
