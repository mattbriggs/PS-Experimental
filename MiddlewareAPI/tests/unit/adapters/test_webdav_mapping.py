"""Unit tests for WebDAV error mapping."""

import httpx

from content_resource_api.adapters.webdav.mapping import map_httpx_error
from content_resource_api.domain.errors import (
    UpstreamProtocolError,
    UpstreamResourceMissing,
    UpstreamTimeout,
    UpstreamUnavailable,
)


class TestMapHttpxError:
    def test_timeout_maps_to_upstream_timeout(self):
        exc = httpx.TimeoutException("timed out")
        result = map_httpx_error(exc)
        assert isinstance(result, UpstreamTimeout)

    def test_connect_error_maps_to_unavailable(self):
        exc = httpx.ConnectError("connection refused")
        result = map_httpx_error(exc)
        assert isinstance(result, UpstreamUnavailable)

    def test_protocol_error_maps_to_protocol_error(self):
        exc = httpx.RemoteProtocolError("bad response")
        result = map_httpx_error(exc)
        assert isinstance(result, UpstreamProtocolError)

    def test_404_status_maps_to_missing(self):
        request = httpx.Request("GET", "http://fake/")
        response = httpx.Response(404, request=request)
        exc = httpx.HTTPStatusError("not found", request=request, response=response)
        result = map_httpx_error(exc)
        assert isinstance(result, UpstreamResourceMissing)

    def test_503_status_maps_to_unavailable(self):
        request = httpx.Request("GET", "http://fake/")
        response = httpx.Response(503, request=request)
        exc = httpx.HTTPStatusError("unavailable", request=request, response=response)
        result = map_httpx_error(exc)
        assert isinstance(result, UpstreamUnavailable)

    def test_500_status_maps_to_protocol_error(self):
        request = httpx.Request("GET", "http://fake/")
        response = httpx.Response(500, request=request)
        exc = httpx.HTTPStatusError("server error", request=request, response=response)
        result = map_httpx_error(exc)
        assert isinstance(result, UpstreamProtocolError)

    def test_unknown_exception_maps_to_protocol_error(self):
        exc = ValueError("unexpected")
        result = map_httpx_error(exc)
        assert isinstance(result, UpstreamProtocolError)
