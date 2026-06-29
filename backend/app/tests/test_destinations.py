import pytest

from app.data.destinations import (
    REGION_TO_ISLAND_GROUP,
    TOP_50_DESTINATIONS,
    get_island_group,
)


class TestGetIslandGroup:
    def test_known_regions(self):
        assert get_island_group("MIMAROPA") == "Luzon"
        assert get_island_group("Central Visayas") == "Visayas"
        assert get_island_group("Davao") == "Mindanao"

    def test_all_regions_are_mapped(self):
        regions_in_data = {d["region"] for d in TOP_50_DESTINATIONS}
        for region in regions_in_data:
            group = get_island_group(region)
            assert group in ("Luzon", "Visayas", "Mindanao", ""), f"{region} -> {group}"

    def test_unknown_region_returns_empty(self):
        assert get_island_group("Unknown") == ""

    def test_empty_string_returns_empty(self):
        assert get_island_group("") == ""

    def test_case_sensitive(self):
        assert get_island_group("mimaropa") == ""
        assert get_island_group("MIMAROPA") == "Luzon"


class TestTop50Destinations:
    def test_has_50_entries(self):
        assert len(TOP_50_DESTINATIONS) == 50

    def test_all_have_required_fields(self):
        for d in TOP_50_DESTINATIONS:
            assert "id" in d
            assert "name" in d
            assert "municipality" in d
            assert "province" in d
            assert "region" in d
            assert "latitude" in d
            assert "longitude" in d
            assert "category" in d

    def test_all_ids_are_unique(self):
        ids = [d["id"] for d in TOP_50_DESTINATIONS]
        assert len(ids) == len(set(ids))

    def test_all_ids_in_range(self):
        for d in TOP_50_DESTINATIONS:
            assert 1 <= d["id"] <= 50

    def test_all_categories_are_valid(self):
        valid = {"beach", "city", "mountain"}
        for d in TOP_50_DESTINATIONS:
            assert d["category"] in valid, f"{d['name']} has category '{d['category']}'"

    def test_mapping_has_all_regions_covered(self):
        regions_in_data = {d["region"] for d in TOP_50_DESTINATIONS}
        mapped_regions = set(REGION_TO_ISLAND_GROUP.keys())
        unmapped = regions_in_data - mapped_regions
        assert not unmapped, f"Regions not in mapping: {unmapped}"

    def test_luzon_has_most_destinations(self):
        luzon_regions = {r for r, g in REGION_TO_ISLAND_GROUP.items() if g == "Luzon"}
        luzon_count = sum(1 for d in TOP_50_DESTINATIONS if d["region"] in luzon_regions)
        assert luzon_count > 20
