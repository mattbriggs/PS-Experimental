"""Content-type validation against registry policy."""

import mimetypes
import re

_SAFE_MEDIA_TYPE = re.compile(
    r"^[a-zA-Z0-9][a-zA-Z0-9!#$&\-^_+.]*\/[a-zA-Z0-9][a-zA-Z0-9!#$&\-^_+.]*$"
)


def guess_content_type(filename: str) -> str | None:
    mime, _ = mimetypes.guess_type(filename)
    return mime


def is_safe_media_type(media_type: str) -> bool:
    return bool(_SAFE_MEDIA_TYPE.match(media_type))
