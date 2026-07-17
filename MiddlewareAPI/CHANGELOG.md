# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-07-17

### Added
- Initial implementation of the Content Resource API
- Ports-and-adapters (hexagonal) architecture with FastAPI and uvicorn
- API key authentication via `X-API-Key` header, loaded from `API_KEY_<id>` env vars
- Registry-gated access to Schematron rules and taxonomy files
- Conditional request support: `If-None-Match` (ETag) and `If-Modified-Since`
  with correct precedence (`If-None-Match` evaluated first)
- Streaming resource delivery with configurable concurrency semaphore
- Resource size limit enforcement (413 when `Content-Length` exceeds registry limit)
- Structured JSON logging with structlog; credentials redacted from all log output
- Prometheus metrics adapter (NoOp in v0.1; real implementation forthcoming)
- Docker multi-stage build (deps / test / runtime) with non-root UID 1000 runtime user
- Docker Compose with `read_only: true` and tmpfs mounts
- Kubernetes manifests: Deployment, Service, ConfigMap, NetworkPolicy, PodDisruptionBudget
- GitHub Actions CI: lint, type-check, SAST (bandit), tests with coverage, Docker build
- Acceptance test suite covering AC-001 through AC-041
- Security tests: traversal (plain/encoded/double-encoded), header injection,
  log redaction, credential conflict, oversized inputs
- Performance benchmark tests (p95 latency targets)
- MkDocs documentation: getting started, API reference, architecture, operations

### Security
- Path traversal prevention with 4-pass iterative decode loop (plain, URL-encoded,
  double-encoded, mixed-case, null bytes, backslash variants all rejected)
- Credential values never included in error responses (safe_detail pattern throughout)
- No upstream WebDAV paths disclosed to clients in any response or header
- Read-only filesystem support in Docker Compose and Kubernetes security context
- `no-new-privileges`, all Linux capabilities dropped in container deployments
