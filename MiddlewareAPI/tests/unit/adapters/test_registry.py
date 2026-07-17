"""Unit tests for registry adapter (snapshot, yaml_loader, reloader)."""


import pytest
import yaml

from content_resource_api.adapters.registry.reloader import RegistrySnapshotManager
from content_resource_api.adapters.registry.snapshot import RegistrySnapshot
from content_resource_api.adapters.registry.yaml_loader import load_registry
from content_resource_api.domain.errors import (
    CategoryNotFound,
    RegistryValidationError,
    ResourceNotRegistered,
)
from content_resource_api.domain.values import CategoryName, PublicFilename

VALID_REGISTRY = {
    "schema_version": "1",
    "categories": [
        {
            "name": "schematron",
            "owner": "team",
            "listing_enabled": True,
            "allowed_scopes": ["schematron:read"],
            "allowed_extensions": [".sch"],
            "size_limit_bytes": 1048576,
            "upstream_root": "schematron/",
            "resources": [
                {
                    "public_filename": "rules.sch",
                    "upstream_object": "schematron/rules.sch",
                    "owner": "team",
                    "enabled": True,
                    "restricted": False,
                },
                {
                    "public_filename": "disabled.sch",
                    "upstream_object": "schematron/disabled.sch",
                    "owner": "team",
                    "enabled": False,
                    "restricted": False,
                },
            ],
        }
    ],
}


@pytest.fixture
def registry_file(tmp_path):
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.dump(VALID_REGISTRY))
    return str(path)


class TestYamlLoader:
    def test_loads_valid_registry(self, registry_file):
        config = load_registry(registry_file)
        assert config.schema_version == "1"
        assert len(config.categories) == 1

    def test_raises_for_missing_file(self):
        with pytest.raises(RegistryValidationError, match="not found"):
            load_registry("/nonexistent/path/registry.yaml")

    def test_raises_for_invalid_yaml(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text(": invalid: yaml: [")
        with pytest.raises(RegistryValidationError):
            load_registry(str(bad))

    def test_raises_for_non_mapping(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("- item1\n- item2\n")
        with pytest.raises(RegistryValidationError):
            load_registry(str(bad))

    def test_raises_for_wrong_schema_version(self, tmp_path):
        data = dict(VALID_REGISTRY)
        data["schema_version"] = "99"
        path = tmp_path / "r.yaml"
        path.write_text(yaml.dump(data))
        with pytest.raises(RegistryValidationError):
            load_registry(str(path))

    def test_raises_for_duplicate_filenames(self, tmp_path):
        data = {
            "schema_version": "1",
            "categories": [{
                "name": "schematron", "owner": "t",
                "listing_enabled": True,
                "allowed_scopes": ["s:read"],
                "allowed_extensions": [".sch"],
                "size_limit_bytes": 1000,
                "upstream_root": "s/",
                "resources": [
                    {"public_filename": "a.sch", "upstream_object": "s/a.sch", "owner": "t", "enabled": True, "restricted": False},
                    {"public_filename": "a.sch", "upstream_object": "s/b.sch", "owner": "t", "enabled": True, "restricted": False},
                ],
            }],
        }
        path = tmp_path / "r.yaml"
        path.write_text(yaml.dump(data))
        with pytest.raises(RegistryValidationError):
            load_registry(str(path))

    def test_raises_for_absolute_upstream(self, tmp_path):
        data = {
            "schema_version": "1",
            "categories": [{
                "name": "schematron", "owner": "t",
                "listing_enabled": True,
                "allowed_scopes": ["s:read"],
                "allowed_extensions": [".sch"],
                "size_limit_bytes": 1000,
                "upstream_root": "s/",
                "resources": [
                    {"public_filename": "a.sch", "upstream_object": "/absolute/path.sch", "owner": "t", "enabled": True, "restricted": False},
                ],
            }],
        }
        path = tmp_path / "r.yaml"
        path.write_text(yaml.dump(data))
        with pytest.raises(RegistryValidationError):
            load_registry(str(path))


class TestRegistrySnapshot:
    @pytest.fixture
    def snapshot(self, registry_file):
        config = load_registry(registry_file)
        return RegistrySnapshot(config)

    def test_category_exists(self, snapshot):
        assert snapshot.category_exists(CategoryName("schematron"))

    def test_category_not_exists(self, snapshot):
        assert not snapshot.category_exists(CategoryName("unknown"))

    def test_list_resources_returns_enabled_only(self, snapshot):
        resources = snapshot.list_resources(CategoryName("schematron"))
        names = [r.public_filename for r in resources]
        assert "rules.sch" in names
        assert "disabled.sch" not in names

    def test_list_resources_sorted_by_name(self, snapshot):
        resources = snapshot.list_resources(CategoryName("schematron"))
        names = [r.public_filename for r in resources]
        assert names == sorted(names)

    def test_list_resources_unknown_category_raises(self, snapshot):
        with pytest.raises(CategoryNotFound):
            snapshot.list_resources(CategoryName("unknown"))

    def test_get_resource_returns_registered(self, snapshot):
        res = snapshot.get_resource(CategoryName("schematron"), PublicFilename("rules.sch"))
        assert res.upstream_object == "schematron/rules.sch"

    def test_get_resource_unknown_category_raises(self, snapshot):
        with pytest.raises(CategoryNotFound):
            snapshot.get_resource(CategoryName("unknown"), PublicFilename("rules.sch"))

    def test_get_resource_disabled_raises(self, snapshot):
        with pytest.raises(ResourceNotRegistered):
            snapshot.get_resource(CategoryName("schematron"), PublicFilename("disabled.sch"))

    def test_get_resource_not_registered_raises(self, snapshot):
        with pytest.raises(ResourceNotRegistered):
            snapshot.get_resource(CategoryName("schematron"), PublicFilename("notexist.sch"))


class TestRegistrySnapshotManager:
    def test_load_and_access(self, registry_file):
        manager = RegistrySnapshotManager(registry_file)
        manager.load()
        snap = manager.snapshot
        assert snap.category_exists(CategoryName("schematron"))

    def test_snapshot_before_load_raises(self, registry_file):
        manager = RegistrySnapshotManager(registry_file)
        with pytest.raises(RuntimeError):
            _ = manager.snapshot

    def test_reload_replaces_snapshot(self, registry_file):
        manager = RegistrySnapshotManager(registry_file)
        manager.load()
        snap1 = manager.snapshot
        manager.reload()
        snap2 = manager.snapshot
        assert snap2 is not snap1

    def test_reload_keeps_previous_on_error(self, registry_file):
        manager = RegistrySnapshotManager(registry_file)
        manager.load()
        good = manager.snapshot
        with open(registry_file, "w") as f:
            f.write("invalid: yaml: content: [")
        with pytest.raises(RegistryValidationError):
            manager.reload()
        assert manager.snapshot is good
