# API Overview

Base path: `/api/resources/v1`

## Authentication

All resource endpoints require an API key in the `X-API-Key` header.

Only one credential mechanism may be provided per request — presenting both `X-API-Key`
and `Authorization: Bearer` in the same request returns **400 Conflict**.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/schematron` | Required | List enabled Schematron rules |
| `GET` | `/schematron/{filename}` | Required | Retrieve a Schematron file |
| `GET` | `/taxonomy` | Required | List enabled taxonomy files |
| `GET` | `/taxonomy/{filename}` | Required | Retrieve a taxonomy file |
| `GET` | `/health/live` | None | Liveness probe |
| `GET` | `/health/ready` | None | Readiness probe |

All other HTTP methods return **405 Method Not Allowed**.

## Listing response schema

```json
{
  "resources": [
    {
      "name": "rules.sch",
      "path": "/schematron/rules.sch",
      "contentType": "application/xml",
      "size": 12345,
      "lastModified": "2024-06-01T00:00:00Z"
    }
  ]
}
```

## Conditional requests

The API honors standard HTTP conditional-request headers:

- **`If-None-Match`** — if the ETag matches the current resource, returns **304 Not Modified** with no body.
  Takes precedence over `If-Modified-Since`.
- **`If-Modified-Since`** — if the resource has not changed since the given date, returns **304 Not Modified**.

## Error schema

```json
{
  "error_code": "MISSING_CREDENTIAL",
  "message": "API key required",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## HTTP status codes

| Code | When |
|---|---|
| 200 | Successful retrieval |
| 304 | Resource not modified (conditional request) |
| 400 | Bad request (conflict, malformed input) |
| 401 | Missing or invalid credential |
| 403 | Valid credential without required scope |
| 404 | Resource or category not found |
| 405 | Write method attempted |
| 413 | Resource exceeds size limit |
| 502 | Upstream protocol error |
| 503 | Upstream unavailable or timeout |

## Correlation IDs

Every response includes an `X-Correlation-ID` header. Supply your own in the request
to correlate distributed traces; the service generates a UUID when the header is absent.
