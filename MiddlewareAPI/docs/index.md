# Content Resource API

The **Content Resource API** is a lightweight, read-only HTTP gateway that exposes
Schematron rules and taxonomy files stored in an internal WebDAV repository to
authorized API consumers.

## Purpose

- Provide scriptable, token-authenticated access to content resources
- Eliminate the need to grant clients direct WebDAV credentials
- Create a controlled, auditable surface area for resource delivery
- Support conditional GET (ETag / If-Modified-Since) for efficient polling

## Quick links

| | |
|---|---|
| [Getting Started](getting-started.md) | Install and run locally in 5 minutes |
| [API Overview](api/overview.md) | Endpoints, schemas, error codes |
| [Architecture](architecture/context.md) | Context, containers, components |
| [Operations](operations/configuration.md) | Config, deployment, secret rotation |

## Resources served

| Category | Path prefix | Content type |
|---|---|---|
| Schematron rules | `/api/resources/v1/schematron/` | `application/xml` |
| Taxonomy files | `/api/resources/v1/taxonomy/` | `application/json` |

## Health probes

| Probe | Endpoint |
|---|---|
| Liveness | `GET /api/resources/v1/health/live` |
| Readiness | `GET /api/resources/v1/health/ready` |
