Here's a draft API spec for the middleware:
Content Resource API — Endpoint Design
Overview
A lightweight, read-only middleware API that provides scoped, authenticated access to specific content resources (schematron rules, taxonomy files) without exposing the underlying WebDAV instance.
Base URL
https://{environment}.heretto.com/api/resources/v1
Authentication
Method: API key via header or OAuth2 bearer token
Header: `Authorization: Bearer

<token>orX-API-Key: `
Keys are scoped per client/integration — each key grants access only to explicitly permitted resource paths.

Endpoints
GET /schematron
List available schematron rule files.
Response:
{
  "resources": [
    {
      "name": "heretto-default.sch",
      "path": "/schematron/heretto-default.sch",
      "lastModified": "2026-07-10T14:32:00Z",
      "size": 12480
    }
  ]
}
GET /schematron/{filename}
Retrieve a specific schematron rule file.
Response: Raw file content
Content-Type: application/xml
Headers: Last-Modified, ETag (for caching/conditional requests)
GET /taxonomy
List available taxonomy files.
Response:
{
  "resources": [
    {
      "name": "product-taxonomy.xml",
      "path": "/taxonomy/product-taxonomy.xml",
      "lastModified": "2026-07-15T09:00:00Z",
      "size": 45200
    }
  ]
}
GET /taxonomy/{filename}
Retrieve a specific taxonomy file.
Response: Raw file content
Content-Type: application/xml or application/json (depending on format)
Headers: Last-Modified, ETag
GET /health
Simple health check for monitoring.
Response:
{
  "status": "ok",
  "upstream": "connected"
}
Common Response Headers
Header
Purpose
ETag
Conditional GET support (If-None-Match)
Last-Modified
Conditional GET support (If-Modified-Since)
Cache-Control
Client-side caching hints
Error Responses
Status
Meaning
401
Missing or invalid credentials
403
Key does not have access to requested resource
404
Resource not found
500
Upstream (WebDAV) unavailable
Design Principles
Read-only — no writes through this API; content authoring stays in the CMS
Scoped — only explicitly registered resource paths are accessible; no directory traversal
Stateless — no sessions; auth on every request
Cacheable — ETags and conditional requests reduce unnecessary transfers for CI/CD polling
Extensible — new resource categories (e.g., /ditaval, /templates) can be added as new path prefixes without restructuring

Example Usage
# List schematron files
curl -H "X-API-Key: abc123" https://pstest.heretto.com/api/resources/v1/schematron

# Fetch a specific rule file
curl -H "X-API-Key: abc123" https://pstest.heretto.com/api/resources/v1/schematron/heretto-default.sch

# Conditional fetch (only if changed)
curl -H "X-API-Key: abc123" \
     -H "If-None-Match: \"a1b2c3\"" \
     https://pstest.heretto.com/api/resources/v1/taxonomy/product-taxonomy.xml
This keeps it dead simple — a few GET endpoints, proper auth, caching support, and no exposure of the broader WebDAV surface. Want me to put this on a Confluence page, or expand any section (e.g., add details on key provisioning, rate limiting, or how the middleware proxies to WebDAV internally)?</token>