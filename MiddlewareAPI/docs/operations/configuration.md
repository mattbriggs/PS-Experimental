# Configuration Reference

All settings use environment variables with the `APP_` prefix (loaded by pydantic-settings).

## Core settings

| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_WEBDAV_BASE_URL` | Yes | — | Base URL of the WebDAV server |
| `APP_WEBDAV_USERNAME` | Yes | — | WebDAV authentication username |
| `APP_WEBDAV_PASSWORD` | Yes | — | WebDAV authentication password |
| `APP_REGISTRY_PATH` | No | `config/registry.yaml` | Path to registry YAML file |
| `APP_LOG_LEVEL` | No | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `APP_METRICS_ENABLED` | No | `true` | Enable Prometheus `/metrics` endpoint |
| `APP_READINESS_REQUIRES_WEBDAV` | No | `true` | WebDAV reachability required for 200 readiness |
| `APP_WEBDAV_TIMEOUT_SECONDS` | No | `30.0` | HTTP timeout for WebDAV requests |
| `APP_WEBDAV_MAX_CONCURRENCY` | No | `10` | Max simultaneous WebDAV connections |
| `APP_AUTH_API_KEY_ENABLED` | No | `true` | Enable API key authentication |

## API key provisioning

API keys are loaded from environment variables matching the pattern:

```
API_KEY_<client-id>=scope1:read,scope2:read
```

The `<client-id>` portion becomes the logged client identifier. Example:

```bash
API_KEY_my-pipeline=schematron:read,taxonomy:read
API_KEY_ci-bot=schematron:read
```

Keys take effect on service restart. There is no runtime hot-reload for keys.

## Registry configuration

The registry YAML file controls which resources are accessible. See
`config/registry.example.yaml` for the full schema. Key constraints enforced at load:

- `schema_version` must be `"1"`
- `upstream_object` paths must be relative (no leading `/`)
- No duplicate `public_filename` values within a category
- All paths are relative to the WebDAV base URL
