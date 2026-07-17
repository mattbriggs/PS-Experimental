# Heretto CCMS — WebDAV Programmatic Access

This session documents how to interact with the Heretto CCMS programmatically via its WebDAV interface, and proposes a RESTful API and contract service to replace that interface if WebDAV is deprecated.

> **Disclaimer:** This is a [prohibited Heretto product or integration](Consulting-Sessions/2026-07-27-WebDav/WARNING.md). It is a research and prototyping effort to explore programmatic access to the Heretto CCMS file system. Do not share with customers.

---

## Background

Heretto CCMS exposes its file system through **WebDAV** (Web Distributed Authoring and Versioning, [RFC 4918](https://www.rfc-editor.org/rfc/rfc4918)). This is the same connection point the oXygen XML Editor uses under the hood. Because WebDAV is a standard HTTP extension, any HTTP client can use it — including cURL, Python scripts, CI/CD pipelines, and custom integrations.

This is **not a formally documented integration pathway** for programmatic use. It is technically available because oXygen depends on it, but using it directly bypasses the application layer and exposes the raw CCMS file system. See the [Security Considerations](#security-considerations) section before building on this.

### WebDAV Base URL

```
https://{organizationId}.heretto.com/webdav/
```

### Key Resource Paths

| Path | Contents |
|------|----------|
| `/webdav/db/organizations/{org}/` | Organization root |
| `/webdav/db/organizations/{org}/content/` | DITA topics, maps, images |
| `/webdav/db/organizations/{org}/taxonomies/` | SKOS taxonomy files |
| `/webdav/db/organizations/{org}/schematron/` | Schematron validation rules |

### Supported HTTP Methods

| Method | Operation |
|--------|-----------|
| `PROPFIND` | List directory contents and file properties |
| `GET` | Download a file |
| `PUT` | Upload or overwrite a file |
| `DELETE` | Delete a file or directory |
| `MKCOL` | Create a new directory (collection) |
| `MOVE` | Rename or relocate a resource |
| `COPY` | Copy a resource |

---

## Authentication

WebDAV requests authenticate with HTTP Basic auth using a **token** generated from the Heretto token management page. Username/password login is not recommended for programmatic access.

### Generate an API Token

1. Sign in to Heretto CCMS.
2. Navigate to:
   ```
   https://{organizationId}.heretto.com/tools/token-management/tokens.xql
   ```
3. Enter a descriptive **Token name** (e.g., `CI-CD Pipeline`, `Schematron Sync`).
4. Click **Create token**.
5. Copy both the **login** and **password (token)** immediately — they cannot be retrieved again.

Store tokens in environment variables or a secrets manager. Never hardcode them in scripts or commit them to source control.

### Environment Variables

All examples in this repository use the following environment variables:

```bash
export HERETTO_ORG="your-org-subdomain"
export HERETTO_USER="your-token-login"
export HERETTO_TOKEN="your-token-password"
```

---

## Security Considerations

> **This integration exposes the raw CCMS file system.** WebDAV itself provides no application-layer guardrails — path traversal, bulk operations, and cross-resource access are all possible with a valid token.

Specific risks:

- **Overly broad access.** A token authenticates to the full organization root unless your server enforces path-based scoping. A single compromised token can read, overwrite, or delete all content.
- **No audit trail by default.** Direct WebDAV access may not flow through the same audit logging as UI operations.
- **Recursive operations.** `PROPFIND` with `Depth: infinity`, bulk uploads, or `DELETE` on a collection can affect thousands of files.
- **Undocumented surface.** Because this is not a formal API, behavior may change without notice as Heretto evolves its infrastructure.

Recommended safeguards:

- Issue **one token per integration** (not one token for everything), so you can revoke individually.
- Scope scripts to only the paths they need (e.g., only the `schematron/` folder for a schematron sync).
- **Never perform recursive deletes** without explicit confirmation logic.
- Log all operations with the path, method, and outcome.
- Rotate tokens on a schedule or when personnel changes.
- Invalidate tokens immediately at `https://{org}.heretto.com/tools/token-management/tokens.xql` when no longer needed.

---

## Repository Structure

```
.
├── README.md                   This file — overview and REST API proposal
├── notes/                      Source notes and research
├── python/                     Python use-case examples
│   ├── README.md
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   └── src/
│       ├── heretto_webdav/     Reusable client module
│       └── use_cases/          Standalone executable examples
└── curl/                       cURL command examples
    ├── README.md
    ├── .env.example
    └── examples/               One script per use case
```

---

## Use Cases Covered

| # | Use Case | Python | cURL |
|---|----------|--------|------|
| 1 | List directory contents | `01_list_resources.py` | `01_list_resources.sh` |
| 2 | Download a file | `02_download_resource.py` | `02_download_resource.sh` |
| 3 | Upload a file | `03_upload_resource.py` | `03_upload_resource.sh` |
| 4 | Delete a file | `04_delete_resource.py` | `04_delete_resource.sh` |
| 5 | Create a directory | `05_create_directory.py` | `05_create_directory.sh` |
| 6 | Export a taxonomy | `06_export_taxonomy.py` | `06_export_taxonomy.sh` |
| 7 | Sync a local directory | `07_sync_directory.py` | `07_backup_deploy_schematron.sh` |

---

## REST API Proposal — WebDAV Deprecation Path

> This section proposes a contract-first RESTful API and contract service that Heretto could build to provide a stable, secure, and versioned replacement for direct WebDAV access.

### Motivation

WebDAV was designed as a document management protocol in 1996. Its original purpose was to let desktop editors (like oXygen) read and write files on a remote server. That use case is valid, but WebDAV has significant drawbacks as a programmatic integration surface:

| Concern | WebDAV Reality | REST API Goal |
|---------|----------------|---------------|
| Discovery | Non-standard XML (multistatus) | Standard JSON, OpenAPI schema |
| Auth | HTTP Basic only | Bearer token, OAuth2 |
| Scope control | Server-side only, no contract | Enforced scopes in token definition |
| Versioning | None | `/api/v1/`, `/api/v2/` |
| Events / webhooks | None | Event subscriptions |
| SDK generation | Manual | Auto-generated from OpenAPI spec |
| Audit logging | Not guaranteed | First-class, per-operation |

### Proposed API Design

The replacement API is organized around **resource types** rather than raw filesystem paths. This decouples integrations from Heretto's internal storage layout.

#### Base URL

```
https://api.heretto.com/v1/
```
or
```
https://{org}.heretto.com/api/v1/
```

#### Authentication

All requests use Bearer token authentication:

```
Authorization: Bearer {token}
```

Tokens are scoped at creation time with an explicit list of permissions and resource roots. The token definition is part of the API contract:

```json
{
  "token_id": "tok_abc123",
  "name": "CI/CD Schematron Sync",
  "principal": "ci-deploy@company.com",
  "scopes": ["content:read", "schematron:read", "schematron:write"],
  "allowed_roots": ["/organizations/acme/schematron/"],
  "expires_at": "2027-01-01T00:00:00Z"
}
```

#### Resource Endpoints

**Content (DITA topics, maps, images)**

```
GET    /v1/content/{+path}        Download file or list directory
PUT    /v1/content/{+path}        Upload or overwrite a file
DELETE /v1/content/{+path}        Delete a file
POST   /v1/content/{+path}/       Create a directory at path
```

**Taxonomies**

```
GET    /v1/taxonomies             List all taxonomies
GET    /v1/taxonomies/{name}      Download a specific taxonomy (SKOS XML)
PUT    /v1/taxonomies/{name}      Upload or replace a taxonomy
DELETE /v1/taxonomies/{name}      Delete a taxonomy
```

**Schematron Rules**

```
GET    /v1/schematron             List all rule sets
GET    /v1/schematron/{name}      Download a rule set
PUT    /v1/schematron/{name}      Upload or replace a rule set
DELETE /v1/schematron/{name}      Delete a rule set
```

**Token Management**

```
GET    /v1/tokens                 List tokens for the calling principal
POST   /v1/tokens                 Create a new token
DELETE /v1/tokens/{id}            Invalidate a token
```

#### Standard Response Format

Successful non-file responses return JSON:

```json
{
  "data": { ... },
  "meta": {
    "request_id": "req_xyz",
    "timestamp": "2026-07-17T14:00:00Z"
  }
}
```

Errors return a consistent structure:

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Token does not have schematron:write scope.",
    "request_id": "req_xyz"
  }
}
```

| HTTP Status | Error Code | Meaning |
|-------------|------------|---------|
| `400` | `INVALID_REQUEST` | Malformed request body or parameters |
| `401` | `UNAUTHENTICATED` | Missing or invalid token |
| `403` | `FORBIDDEN` | Token lacks required scope |
| `404` | `NOT_FOUND` | Resource does not exist (or is out-of-scope) |
| `409` | `CONFLICT` | Parent path does not exist; resource locked |
| `429` | `RATE_LIMITED` | Request rate exceeded |
| `500` | `INTERNAL_ERROR` | Server-side failure |

#### Directory Listing Response

`GET /v1/content/topics/` returns:

```json
{
  "data": {
    "path": "/organizations/acme/content/topics/",
    "type": "directory",
    "children": [
      { "name": "install-guide.dita", "type": "file", "size": 4201, "last_modified": "2026-06-10T08:22:00Z" },
      { "name": "config-guide.dita",  "type": "file", "size": 3100, "last_modified": "2026-07-01T12:00:00Z" },
      { "name": "advanced/",           "type": "directory" }
    ]
  }
}
```

### OpenAPI Contract

The API would be specified as an **OpenAPI 3.1 document** (`openapi.yaml`). This enables:

- Auto-generated client SDKs (Python, TypeScript, Java, Go)
- Mock servers for integration testing without a live CCMS
- Inline documentation via Swagger UI or Redoc
- Contract testing in CI/CD pipelines

Minimal contract excerpt:

```yaml
openapi: "3.1.0"
info:
  title: Heretto Content API
  version: "1.0.0"
  description: RESTful access to Heretto CCMS resources.

servers:
  - url: https://{org}.heretto.com/api/v1
    variables:
      org:
        default: your-org

security:
  - BearerToken: []

components:
  securitySchemes:
    BearerToken:
      type: http
      scheme: bearer
      bearerFormat: HRT  # Heretto Resource Token

paths:
  /content/{path}:
    get:
      summary: Download a file or list a directory
      parameters:
        - name: path
          in: path
          required: true
          schema: { type: string }
      responses:
        "200":
          description: File content or directory listing
        "404":
          $ref: "#/components/responses/NotFound"

  /taxonomies/{name}:
    get:
      summary: Download a taxonomy by name
      parameters:
        - name: name
          in: path
          required: true
          schema: { type: string }
      responses:
        "200":
          description: SKOS XML taxonomy file
          content:
            application/xml: {}
    put:
      summary: Upload or replace a taxonomy
      requestBody:
        required: true
        content:
          application/xml: {}
      responses:
        "201": { description: Created }
        "204": { description: Updated }
```

### Migration Path for Integrations

When WebDAV is deprecated, existing integrations can migrate by:

1. **Updating the base URL** — replace `https://{org}.heretto.com/webdav/db/organizations/{org}/` with `https://{org}.heretto.com/api/v1/`.
2. **Updating auth headers** — replace HTTP Basic (`Authorization: Basic ...`) with Bearer (`Authorization: Bearer ...`).
3. **Replacing PROPFIND with GET** — `GET /v1/content/topics/` replaces `PROPFIND` with `Depth: 1`.
4. **Using JSON instead of multistatus XML** — directory listings are plain JSON arrays.

A compatibility shim (a thin server that accepts WebDAV requests and proxies them to the new REST API) could smooth the transition for oXygen and other DAV clients while the REST API matures.

### Implementation Recommendations for Heretto

| Priority | Recommendation |
|----------|----------------|
| 1 | Publish an OpenAPI 3.1 spec as the contract before writing implementation code |
| 2 | Implement scoped tokens (permissions + allowed roots) at the API gateway layer |
| 3 | Add per-request audit logging (principal, method, path, outcome) from day one |
| 4 | Version the API (`/v1/`) and commit to a deprecation policy for future versions |
| 5 | Provide a WebDAV-to-REST compatibility shim for oXygen transition |
| 6 | Publish auto-generated SDK packages (Python, TypeScript) from the OpenAPI spec |
| 7 | Add a webhook/event system for content change notifications |

---

## Troubleshooting

| Symptom | Cause | Resolution |
|---------|-------|------------|
| `401 Unauthorized` | Invalid or expired token | Regenerate at `/tools/token-management/tokens.xql` |
| `403 Forbidden` | Insufficient CCMS role permissions | Verify your role grants access to the target path |
| `404 Not Found` | Wrong path or resource missing | PROPFIND the parent directory to confirm the path |
| `405 Method Not Allowed` | WebDAV not enabled | Contact Heretto support |
| `409 Conflict` on PUT | Parent directory missing | Run MKCOL on the parent path first |

---

## References

- [RFC 4918 — WebDAV](https://www.rfc-editor.org/rfc/rfc4918)
- [Heretto Token Management](https://help.heretto.com) — see oXygen integration docs for token generation steps
- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- Notes: [heretto-webdav-programmatic-access.md](notes/heretto-webdav-programmatic-access.md)
- Notes: [webdav-notes.md](notes/webdav-notes.md)
