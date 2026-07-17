# Getting Started

## Prerequisites

- Python 3.12+
- Access to a WebDAV repository containing Schematron rules and/or taxonomy files
- An API key provisioned for your client

## Local development

```bash
git clone <repo>
cd MiddlewareAPI
make install          # creates .venv, installs all dependencies
cp .env.example .env  # edit with your WebDAV credentials and API keys
cp config/registry.example.yaml config/registry.yaml  # configure resources
make test             # run full test suite
make run              # start on :8080
```

## Docker Compose

```bash
cp .env.example .env  # fill in WEBDAV_PASSWORD and API_KEY_* values
docker compose up -d  # starts api + webdav services
```

## First request

```bash
# List available Schematron rules
curl -H "X-API-Key: <your-key>" http://localhost:8080/api/resources/v1/schematron

# Download a specific rule file
curl -H "X-API-Key: <your-key>" \
  http://localhost:8080/api/resources/v1/schematron/rules.sch \
  -o rules.sch
```

## Provisioning an API key

Add an environment variable to `.env` (or secret store) before starting the service:

```
API_KEY_my-service=schematron:read,taxonomy:read
```

The key name after `API_KEY_` becomes the client ID. The value is a comma-separated list of scopes. Restart the service for the new key to take effect.
