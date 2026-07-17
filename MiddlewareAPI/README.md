# Content Resource API

A lightweight, read-only middleware service providing authenticated machine access to approved content resources stored in an internal WebDAV repository.

## Supported routes

```
GET /api/resources/v1/schematron              List available Schematron resources
GET /api/resources/v1/schematron/{filename}   Retrieve a Schematron resource
GET /api/resources/v1/taxonomy               List available taxonomy resources
GET /api/resources/v1/taxonomy/{filename}    Retrieve a taxonomy resource
GET /api/resources/v1/health/live            Liveness probe
GET /api/resources/v1/health/ready           Readiness probe
```

**Read-only guarantee:** No write operations are exposed. The service cannot create, modify, delete, move, or browse upstream content.  
**No arbitrary path access:** Public identifiers are resolved through a registry. Clients cannot request arbitrary WebDAV paths.

## Prerequisites

- Python 3.12+
- Docker and Docker Compose (for containerized development)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,docs]"
```

## Configuration

Copy `.env.example` to `.env` and adjust values. API keys are injected as environment variables:

```
API_KEY_<client-id>=scope1:read,scope2:read
```

## Registry validation

```bash
python -m scripts.validate_registry
```

## Running

```bash
python -m content_resource_api
# or
uvicorn "content_resource_api.interface.http.app:create_app" --factory --port 8080
```

## Quality checks

```bash
make lint          # Ruff lint and format check
make type-check    # mypy strict
make test          # pytest
make coverage      # Coverage with threshold
make security      # Bandit
```

## Docker Compose

```bash
docker compose up --build                     # API + WebDAV
docker compose --profile observability up     # + Prometheus + Grafana
docker compose down -v                        # Tear down
```

## Security disclosure

Report security issues privately to the platform security team. Do not open public issues for security vulnerabilities.
