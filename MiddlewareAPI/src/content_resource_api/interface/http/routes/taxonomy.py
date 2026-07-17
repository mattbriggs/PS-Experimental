"""Taxonomy category routes."""

from content_resource_api.interface.http.routes._category_router import make_category_router

router = make_category_router("taxonomy", "/taxonomy", ["taxonomy"])
