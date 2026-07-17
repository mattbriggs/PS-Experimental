"""Unit tests for filename validation."""

import pytest

from content_resource_api.domain.errors import InvalidResourceIdentifier
from content_resource_api.domain.validators import validate_category_name, validate_public_filename


class TestValidatePublicFilename:
    def test_valid_simple_filename(self):
        assert validate_public_filename("base-rules.sch") == "base-rules.sch"

    def test_rejects_empty(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_public_filename("")

    def test_rejects_dot(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_public_filename(".")

    def test_rejects_dotdot(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_public_filename("..")

    def test_rejects_slash(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_public_filename("../evil.sch")

    def test_rejects_null_byte(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_public_filename("file\x00.sch")

    def test_rejects_encoded_traversal(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_public_filename("..%2Fevil.sch")

    def test_rejects_double_encoded_traversal(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_public_filename("..%252Fevil.sch")

    def test_rejects_overlength(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_public_filename("a" * 201, max_length=200)

    def test_accepts_extension_filename(self):
        assert validate_public_filename("product-taxonomy.json") == "product-taxonomy.json"

    def test_rejects_invalid_percent_encoding(self):
        # %80 decodes to byte 0x80 which is not valid UTF-8 — triggers strict-mode error
        with pytest.raises(InvalidResourceIdentifier, match="percent-encoding"):
            validate_public_filename("%80rules.sch")

    def test_rejects_empty_after_decoding(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_public_filename("%00")

    def test_rejects_encoded_null_byte(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_public_filename("file%00.sch")


class TestValidateCategoryName:
    def test_valid_lowercase(self):
        assert validate_category_name("schematron") == "schematron"

    def test_valid_with_hyphen(self):
        assert validate_category_name("tax-onomy") == "tax-onomy"

    def test_rejects_empty(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_category_name("")

    def test_rejects_uppercase(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_category_name("Schematron")

    def test_rejects_leading_hyphen(self):
        with pytest.raises(InvalidResourceIdentifier):
            validate_category_name("-bad")
