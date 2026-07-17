"""Load and validate a registry YAML file into a RegistryConfig."""

import yaml
from pydantic import ValidationError

from content_resource_api.config.registry_models import RegistryConfig
from content_resource_api.domain.errors import RegistryValidationError


def load_registry(path: str) -> RegistryConfig:
    try:
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except FileNotFoundError:
        raise RegistryValidationError(f"Registry file not found: {path!r}") from None
    except yaml.YAMLError as exc:
        raise RegistryValidationError(f"Registry YAML parse error: {exc}") from exc

    if not isinstance(raw, dict):
        raise RegistryValidationError("Registry must be a YAML mapping")

    try:
        return RegistryConfig.model_validate(raw)
    except ValidationError as exc:
        raise RegistryValidationError(f"Registry validation failed: {exc}") from exc
