"""Validate the configured registry file and report errors."""

import sys

from content_resource_api.adapters.registry.yaml_loader import load_registry
from content_resource_api.config.settings import Settings
from content_resource_api.domain.errors import RegistryValidationError


def main() -> int:
    settings = Settings()
    try:
        config = load_registry(settings.registry_path)
        print(f"Registry valid: {len(config.categories)} categories loaded.")
        for cat in config.categories:
            print(f"  {cat.name}: {len(cat.resources)} resources")
        return 0
    except RegistryValidationError as exc:
        print(f"Registry invalid: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
