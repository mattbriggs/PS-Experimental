"""Value types and typed aliases."""

from typing import NewType

CategoryName = NewType("CategoryName", str)
PublicFilename = NewType("PublicFilename", str)
UpstreamResourceRef = NewType("UpstreamResourceRef", str)
