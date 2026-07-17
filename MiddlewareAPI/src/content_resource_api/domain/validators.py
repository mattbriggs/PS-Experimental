"""Filename and public-identifier validation.

Validation is bounded, non-normalizing, and terminates before any
registry lookup or WebDAV access.
"""

import re
import urllib.parse

from content_resource_api.domain.errors import InvalidResourceIdentifier

_TRAVERSAL_TOKENS = frozenset([".", ".."])
_FORBIDDEN_CHARS = frozenset(["/", "\\", "\x00"])
_ENCODED_SEPARATOR = re.compile(r"%2[Ff]|%5[Cc]", re.IGNORECASE)
_ENCODED_DOT = re.compile(r"%2[Ee]", re.IGNORECASE)


def _decode_once(value: str) -> str:
    try:
        return urllib.parse.unquote(value, errors="strict")
    except Exception:
        raise InvalidResourceIdentifier(
            "Filename contains invalid percent-encoding",
            safe_detail="Invalid percent-encoding in filename",
        ) from None


def validate_public_filename(filename: str, max_length: int = 200) -> str:
    """Validate and return the filename, or raise InvalidResourceIdentifier.

    Performs up to 3 percent-decode passes so plain, encoded, and
    double-encoded traversal attempts are all detected before any registry
    lookup or WebDAV access.  Does not normalize the filename.
    """
    if not filename:
        raise InvalidResourceIdentifier("Empty filename", safe_detail="Filename is empty")

    if len(filename) > max_length:
        raise InvalidResourceIdentifier(
            f"Filename exceeds {max_length} characters",
            safe_detail="Filename is too long",
        )

    current = filename
    for _ in range(4):  # raw form + up to 3 decode passes
        if _ENCODED_SEPARATOR.search(current):
            raise InvalidResourceIdentifier(
                "Encoded path separator in filename",
                safe_detail="Invalid characters in filename",
            )

        for char in _FORBIDDEN_CHARS:
            if char in current:
                raise InvalidResourceIdentifier(
                    f"Forbidden character in filename: {char!r}",
                    safe_detail="Invalid characters in filename",
                )

        if current in _TRAVERSAL_TOKENS:
            raise InvalidResourceIdentifier(
                "Traversal token in filename",
                safe_detail="Invalid filename",
            )

        decoded = _decode_once(current)
        if decoded == current:
            break
        current = decoded

    if not current:
        raise InvalidResourceIdentifier(
            "Filename is empty after decoding", safe_detail="Empty filename"
        )

    return current


def validate_category_name(name: str) -> str:
    """Validate a category name segment."""
    if not name or not re.match(r"^[a-z0-9][a-z0-9_-]*$", name):
        raise InvalidResourceIdentifier(
            f"Invalid category name: {name!r}",
            safe_detail="Invalid category name",
        )
    return name
