# Release Checklist

## Pre-release

### Code quality
- [ ] All tests pass: `make test`
- [ ] Coverage meets thresholds: `make coverage`
- [ ] No lint errors: `make lint`
- [ ] No type errors: `make typecheck`
- [ ] Security scan clean: `make security`

### Documentation
- [ ] CHANGELOG.md updated for this version
- [ ] API docs reflect any schema or endpoint changes
- [ ] Configuration reference updated for any new settings

### Registry
- [ ] Production registry validated: `python scripts/validate_registry.py config/registry.yaml`
- [ ] No absolute upstream paths in registry
- [ ] No duplicate public filenames within a category

### Secrets
- [ ] API keys for all active clients provisioned in secret store
- [ ] WebDAV credentials valid; tested against production WebDAV
- [ ] Old/rotated keys removed from secret store

### Infrastructure
- [ ] Docker image builds: `docker build --target runtime .`
- [ ] K8s manifests dry-run: `kubectl apply --dry-run=client -f deploy/kubernetes/`
- [ ] Read-only root verified: container starts without filesystem write errors
- [ ] Liveness probe: 200 within 30s of container start
- [ ] Readiness probe: 200 once WebDAV is reachable

## Deployment

- [ ] Deploy to staging; smoke test: `curl -H "X-API-Key: $KEY" .../api/resources/v1/schematron`
- [ ] Audit logs appear in structured JSON format
- [ ] 304 returned for repeat requests with matching ETag
- [ ] Monitor 5xx rate during rollout (target: 0%)
- [ ] Git tag: `git tag -s v0.1.0 -m "Release 0.1.0"`

## Post-release

- [ ] Confirm clients are operational with new endpoints
- [ ] Archive release artifacts (SBOM, Docker image digest, coverage report)
- [ ] Close release issue/ticket
- [ ] Notify stakeholders
