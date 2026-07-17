"""Unit tests for conditional request evaluation."""

from datetime import UTC, datetime

import pytest

from content_resource_api.domain.conditional_requests import ConditionalRequestService
from content_resource_api.domain.models import ResourceMetadata


@pytest.fixture
def service():
    return ConditionalRequestService()


@pytest.fixture
def metadata():
    return ResourceMetadata(
        etag='"abc123"',
        last_modified=datetime(2024, 1, 1, tzinfo=UTC),
        content_type="application/xml",
        content_length=100,
    )


class TestETagPrecedence:
    def test_matching_etag_returns_not_modified(self, service, metadata):
        result = service.evaluate(metadata, if_none_match='"abc123"', if_modified_since=None)
        assert result.not_modified is True

    def test_nonmatching_etag_returns_modified(self, service, metadata):
        result = service.evaluate(metadata, if_none_match='"different"', if_modified_since=None)
        assert result.not_modified is False

    def test_wildcard_etag_matches(self, service, metadata):
        result = service.evaluate(metadata, if_none_match="*", if_modified_since=None)
        assert result.not_modified is True

    def test_etag_takes_precedence_over_date(self, service, metadata):
        future = datetime(2030, 1, 1, tzinfo=UTC)
        result = service.evaluate(metadata, if_none_match='"abc123"', if_modified_since=future)
        assert result.not_modified is True

    def test_no_validators_returns_modified(self, service, metadata):
        result = service.evaluate(metadata, if_none_match=None, if_modified_since=None)
        assert result.not_modified is False
