"""Authorization policy."""

from content_resource_api.domain.models import (
    AuthorizationDecision,
    ClientPrincipal,
    RegisteredResource,
)


class AuthorizationService:
    """Evaluates whether a principal may access a resource."""

    def authorize(
        self,
        principal: ClientPrincipal,
        resource: RegisteredResource,
    ) -> AuthorizationDecision:
        if not resource.enabled:
            return AuthorizationDecision(allowed=False, reason="Resource is disabled")

        if not principal.has_scope(resource.required_scope):
            return AuthorizationDecision(
                allowed=False,
                reason=f"Principal lacks required scope: {resource.required_scope}",
            )

        return AuthorizationDecision(allowed=True, reason="Authorized")
