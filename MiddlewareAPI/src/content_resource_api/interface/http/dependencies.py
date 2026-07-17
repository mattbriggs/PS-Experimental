"""FastAPI dependency injection functions."""

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request

from content_resource_api.domain.models import ClientPrincipal, CorrelationId
from content_resource_api.interface.http.headers import (
    extract_api_key_credential,
    extract_bearer_credential,
    extract_correlation_id,
)

if TYPE_CHECKING:
    from content_resource_api.adapters.authentication.composite import (
        CompositeAuthenticationAdapter,
    )


async def get_correlation_id(request: Request) -> CorrelationId:
    return extract_correlation_id(request)


async def get_principal(request: Request) -> ClientPrincipal:
    composite: CompositeAuthenticationAdapter = request.app.state.auth_adapter
    api_key_cred = extract_api_key_credential(request)
    bearer_cred = extract_bearer_credential(request)
    return await composite.authenticate(api_key_cred, bearer_cred)


CorrelationIdDep = Annotated[CorrelationId, Depends(get_correlation_id)]
PrincipalDep = Annotated[ClientPrincipal, Depends(get_principal)]
