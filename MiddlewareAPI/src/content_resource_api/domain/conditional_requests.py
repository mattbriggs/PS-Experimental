"""Conditional request evaluation (ETag and Last-Modified)."""

from datetime import datetime

from content_resource_api.domain.models import CacheDecision, ResourceMetadata


class ConditionalRequestService:
    """Evaluates HTTP conditional request validators against resource metadata."""

    def evaluate(
        self,
        metadata: ResourceMetadata,
        if_none_match: str | None,
        if_modified_since: datetime | None,
    ) -> CacheDecision:
        if if_none_match is not None and metadata.etag is not None:
            matched = self._etag_matches(if_none_match, metadata.etag)
            return CacheDecision(
                not_modified=matched,
                etag=metadata.etag,
                last_modified=metadata.last_modified,
            )

        if if_modified_since is not None and metadata.last_modified is not None:
            not_modified = metadata.last_modified <= if_modified_since
            return CacheDecision(
                not_modified=not_modified,
                etag=metadata.etag,
                last_modified=metadata.last_modified,
            )

        return CacheDecision(
            not_modified=False,
            etag=metadata.etag,
            last_modified=metadata.last_modified,
        )

    @staticmethod
    def _etag_matches(if_none_match: str, etag: str) -> bool:
        if if_none_match.strip() == "*":
            return True
        candidates = [v.strip().strip('"') for v in if_none_match.split(",")]
        clean_etag = etag.strip().strip('"')
        return clean_etag in candidates
