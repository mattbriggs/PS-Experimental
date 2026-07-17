#!/usr/bin/env python3
"""Export the OpenAPI schema to openapi.json for documentation builds."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

os.environ.setdefault("APP_WEBDAV_BASE_URL", "http://localhost")
os.environ.setdefault("APP_WEBDAV_USERNAME", "user")
os.environ.setdefault("APP_WEBDAV_PASSWORD", "pass")
os.environ.setdefault("APP_REGISTRY_PATH", "config/registry.example.yaml")

from content_resource_api.config.settings import Settings
from content_resource_api.interface.http.app import create_app

settings = Settings()
app = create_app(settings=settings)
schema = app.openapi()

out = Path("openapi.json")
out.write_text(json.dumps(schema, indent=2))
print(f"Written {out} ({len(schema)} top-level keys, {len(schema.get('paths', {}))} paths)")
