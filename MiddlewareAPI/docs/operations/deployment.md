# Deployment

## Docker Compose

```bash
# Start production services
docker compose up -d --build

# Include observability stack (Prometheus + Grafana)
docker compose --profile observability up -d

# View API logs
docker compose logs -f api
```

The `compose.yaml` enforces `read_only: true` on the API container. Two tmpfs mounts
provide writable scratch space: `/tmp` and `/tmp/app`.

## Kubernetes

Apply manifests in dependency order:

```bash
kubectl apply -f deploy/kubernetes/namespace.yaml
kubectl apply -f deploy/kubernetes/configmap.yaml
kubectl apply -f deploy/kubernetes/secret-provider.yaml   # or a plain Secret
kubectl apply -f deploy/kubernetes/deployment.yaml
kubectl apply -f deploy/kubernetes/service.yaml
kubectl apply -f deploy/kubernetes/network-policy.yaml
kubectl apply -f deploy/kubernetes/pod-disruption-budget.yaml
```

The deployment pod spec sets:
- `readOnlyRootFilesystem: true`
- `runAsNonRoot: true` (UID 1000)
- `allowPrivilegeEscalation: false`
- All capabilities dropped

## Zero-downtime rollout

The Deployment uses `RollingUpdate` strategy with `minAvailable: 1` enforced by the
PodDisruptionBudget. Scale to at least 2 replicas before maintenance windows.

```bash
kubectl rollout status deployment/content-resource-api -n content-resources
kubectl rollout undo deployment/content-resource-api -n content-resources  # rollback
```

## Smoke test

```bash
curl -H "X-API-Key: $KEY" https://<host>/api/resources/v1/health/ready
curl -H "X-API-Key: $KEY" https://<host>/api/resources/v1/schematron
```
