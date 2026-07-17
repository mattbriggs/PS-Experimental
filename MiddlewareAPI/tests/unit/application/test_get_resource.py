"""Unit tests for GetResourceHandler."""

from datetime import UTC, datetime

import pytest

from content_resource_api.application.commands import GetResourceCommand
from content_resource_api.application.get_resource import GetResourceHandler
from content_resource_api.application.results import NotModifiedResult, ResourceStreamResult
from content_resource_api.domain.authorization import AuthorizationService
from content_resource_api.domain.conditional_requests import ConditionalRequestService
from content_resource_api.domain.errors import AuthorizationError, ResourceNotRegistered
from content_resource_api.domain.models import CorrelationId, RegisteredResource, ResourceMetadata
from tests.doubles.content_repository import FakeContentRepository

RESOURCE = RegisteredResource(
    category="schematron",
    public_filename="rules.sch",
    upstream_object="schematron/rules.sch",
    owner="team",
    enabled=True,
    restricted=False,
    allowed_extensions=(".sch",),
    size_limit_bytes=1048576,
    required_scope="schematron:read",
)

METADATA = ResourceMetadata(
    etag='"abc123"',
    last_modified=datetime(2024, 1, 1, tzinfo=UTC),
    content_type="application/xml",
    content_length=100,
)


class FakeRegistry:
    def __init__(self, resource=RESOURCE, raise_not_registered=False):
        self._resource = resource
        self._raise = raise_not_registered

    def get_resource(self, category, filename):
        if self._raise:
            raise ResourceNotRegistered("not found")
        return self._resource

    def list_resources(self, category):
        return (self._resource,)

    def category_exists(self, category):
        return True


def make_command(**kwargs):
    defaults = {
        "category": "schematron",
        "filename": "rules.sch",
        "correlation_id": CorrelationId(value="test-cid"),
        "principal_id": "client1",
        "principal_scopes": frozenset(["schematron:read"]),
    }
    defaults.update(kwargs)
    return GetResourceCommand(**defaults)


@pytest.fixture
def handler():
    repo = FakeContentRepository(metadata=METADATA, content=b"<rules/>")
    return GetResourceHandler(
        registry=FakeRegistry(),
        repository=repo,
        auth_service=AuthorizationService(),
        cond_service=ConditionalRequestService(),
    )


class TestGetResourceHandler:
    async def test_returns_stream_result(self, handler):
        cmd = make_command()
        result = await handler.handle(cmd)
        assert isinstance(result, ResourceStreamResult)

    async def test_returns_not_modified_on_matching_etag(self, handler):
        cmd = make_command(if_none_match='"abc123"')
        result = await handler.handle(cmd)
        assert isinstance(result, NotModifiedResult)
        assert result.etag == '"abc123"'

    async def test_raises_authorization_error_without_scope(self):
        repo = FakeContentRepository(metadata=METADATA)
        handler = GetResourceHandler(
            registry=FakeRegistry(),
            repository=repo,
            auth_service=AuthorizationService(),
            cond_service=ConditionalRequestService(),
        )
        cmd = make_command(principal_scopes=frozenset(["wrong:scope"]))
        with pytest.raises(AuthorizationError):
            await handler.handle(cmd)

    async def test_raises_resource_not_registered(self):
        repo = FakeContentRepository(metadata=METADATA)
        handler = GetResourceHandler(
            registry=FakeRegistry(raise_not_registered=True),
            repository=repo,
            auth_service=AuthorizationService(),
            cond_service=ConditionalRequestService(),
        )
        cmd = make_command()
        with pytest.raises(ResourceNotRegistered):
            await handler.handle(cmd)

    async def test_date_validator_returns_not_modified(self, handler):
        future = datetime(2030, 1, 1, tzinfo=UTC)
        cmd = make_command(if_modified_since=future)
        result = await handler.handle(cmd)
        assert isinstance(result, NotModifiedResult)
