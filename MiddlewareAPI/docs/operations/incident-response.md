# Incident Response

## WebDAV outage

**Symptoms**: `GET /health/ready` returns 503; resource retrieval returns 503.

**Response**:
1. Confirm WebDAV is reachable from the API pod/container
2. Review logs for `upstream_unavailable` or `upstream_timeout` events
3. The liveness probe (`/health/live`) remains 200 — load balancer keeps routing

**Note**: The API does not cache upstream content. All retrieval requests fail during
a WebDAV outage.

## Authentication failure surge

**Symptoms**: Spike in 401 responses; `authentication_failed` audit events.

**Response**:
1. Check whether a credential rotation is underway
2. Use the `correlation_id` in error logs to identify the affected client
3. If unauthorized access is suspected, remove the suspect key and restart immediately

## Elevated 5xx rate

**Response**:
1. Check `GET /health/ready` — if 503, follow the WebDAV outage playbook
2. Review structured logs for error patterns (look for `error_code` field)
3. If a restart is needed:
   ```bash
   kubectl rollout restart deployment/content-resource-api -n content-resources
   ```
4. To roll back a bad release:
   ```bash
   kubectl rollout undo deployment/content-resource-api -n content-resources
   ```
