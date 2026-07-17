"""Unit tests for content_types module."""

from content_resource_api.domain.content_types import guess_content_type, is_safe_media_type


class TestGuessContentType:
    def test_xml_extension(self):
        result = guess_content_type("rules.xml")
        assert result is not None and "xml" in result

    def test_json_extension(self):
        result = guess_content_type("data.json")
        assert result is not None and "json" in result

    def test_unknown_extension(self):
        result = guess_content_type("file.xyz123")
        assert result is None


class TestIsSafeMediaType:
    def test_application_xml_is_safe(self):
        assert is_safe_media_type("application/xml") is True

    def test_application_json_is_safe(self):
        assert is_safe_media_type("application/json") is True

    def test_empty_string_not_safe(self):
        assert is_safe_media_type("") is False

    def test_spaces_not_safe(self):
        assert is_safe_media_type("text/ html") is False
