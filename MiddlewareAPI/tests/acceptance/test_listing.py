"""Acceptance tests: AC-013 through AC-016 — Listing."""


class TestAC013SchematronListing:
    """AC-013: Listing returns 200, resources in ascending filename order."""

    def test_listing_returns_200(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron", headers=auth_headers)
        assert r.status_code == 200

    def test_response_has_resources_key(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron", headers=auth_headers)
        assert "resources" in r.json()

    def test_resources_ordered_by_name(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron", headers=auth_headers)
        names = [item["name"] for item in r.json()["resources"]]
        assert names == sorted(names)


class TestAC014DisabledResourcesExcluded:
    """AC-014: Disabled resources absent from listing."""

    def test_disabled_resource_excluded(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron", headers=auth_headers)
        names = [item["name"] for item in r.json()["resources"]]
        assert "disabled-rules.sch" not in names


class TestAC015EmptyListing:
    """AC-015: Category with no visible resources returns 200 with empty list."""

    def test_taxonomy_listing_returns_200(self, client, auth_headers):
        r = client.get("/api/resources/v1/taxonomy", headers=auth_headers)
        assert r.status_code == 200

    def test_empty_listing_has_resources_array(self, client, auth_headers):
        r = client.get("/api/resources/v1/taxonomy", headers=auth_headers)
        body = r.json()
        assert "resources" in body
        assert isinstance(body["resources"], list)


class TestAC016ListingMetadataContract:
    """AC-016: Each listing item has name and path fields."""

    def test_items_have_name_and_path(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron", headers=auth_headers)
        for item in r.json()["resources"]:
            assert "name" in item
            assert "path" in item

    def test_path_is_public_not_upstream(self, client, auth_headers):
        r = client.get("/api/resources/v1/schematron", headers=auth_headers)
        for item in r.json()["resources"]:
            path = item["path"]
            assert path.startswith("/schematron/")
            assert "schematron/" not in path.replace("/schematron/", "", 1)
