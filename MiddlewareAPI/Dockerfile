# syntax=docker/dockerfile:1.6
ARG PYTHON_VERSION=3.12
ARG APPUSER_UID=1000

# ── deps stage ─────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS deps

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --upgrade pip && pip wheel --no-cache-dir --wheel-dir /wheels ".[dev]"

# ── test stage ─────────────────────────────────────────────────────────────────
FROM deps AS test

RUN pip install --no-cache-dir --find-links /wheels -e ".[dev]"
COPY . .
ENTRYPOINT ["pytest"]
CMD ["tests/unit/", "tests/integration/", "-q", "--tb=short"]

# ── runtime stage ──────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime

ARG APPUSER_UID
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

LABEL org.opencontainers.image.title="Content Resource API"
LABEL org.opencontainers.image.description="Read-only content resource gateway over WebDAV"
LABEL org.opencontainers.image.vendor="Heretto"
LABEL com.heretto.component="content-resource-api"
LABEL com.heretto.team="platform-services"

RUN groupadd -r appuser && useradd -r -g appuser -u ${APPUSER_UID} appuser

WORKDIR /app

COPY --from=deps /wheels /wheels
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY config/ ./config/

RUN pip install --no-cache-dir --find-links /wheels "." && rm -rf /wheels

RUN mkdir -p /tmp/app /app/config && chown -R appuser:appuser /app /tmp/app

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/resources/v1/health/live')" || exit 1

ENTRYPOINT ["python", "-m", "content_resource_api"]
