"""Application-wide constants."""

API_VERSION = "v1"
API_PREFIX = f"/api/resources/{API_VERSION}"

CORRELATION_ID_HEADER = "X-Correlation-ID"
API_KEY_HEADER = "X-API-Key"

SAFE_CORRELATION_ID_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "-_."
)

REGISTRY_SCHEMA_VERSION = "1"
AUDIT_SCHEMA_VERSION = "1"
MAX_DECODE_PASSES = 3

SCOPE_SEPARATOR = ":"
SCOPE_ACTION_READ = "read"
