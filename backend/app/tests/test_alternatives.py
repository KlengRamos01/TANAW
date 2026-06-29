import pytest

from app.services.alternatives import (
    _haversine_km,
    _travel_time_estimate,
    _candidate_risk,
    find_alternatives,
)


class TestHaversineKm:
    def test_same_point_zero_distance(self):
        assert _haversine_km(10.0, 120.0, 10.0, 120.0) == 0.0

    def test_north_south_roughly_111km_per_degree(self):
        dist = _haversine_km(10.0, 120.0, 11.0, 120.0)
        assert 110 < dist < 112

    def test_el_nido_to_coron_known_distance(self):
        dist = _haversine_km(11.1958, 119.4092, 11.9988, 120.2019)
        assert 120 < dist < 130

    def test_manila_to_baguio(self):
        dist = _haversine_km(14.5995, 120.9842, 16.4023, 120.5960)
        assert 180 < dist < 230

    def test_symmetric(self):
        d1 = _haversine_km(15.0, 121.0, 16.0, 122.0)
        d2 = _haversine_km(16.0, 122.0, 15.0, 121.0)
        assert d1 == d2


class TestTravelTimeEstimate:
    def test_under_1hr_returns_minutes(self):
        result = _travel_time_estimate(30)
        assert result == "30 min"

    def test_exactly_60km_returns_1hr(self):
        result = _travel_time_estimate(60)
        assert result == "1 hr"

    def test_between_1_and_2_hours_returns_1hr(self):
        result = _travel_time_estimate(90)
        assert result == "1 hr"

    def test_120km_returns_2_hrs(self):
        result = _travel_time_estimate(120)
        assert result == "2 hrs"

    def test_long_distance(self):
        result = _travel_time_estimate(350)
        assert result == "6 hrs"

    def test_zero_distance(self):
        result = _travel_time_estimate(0)
        assert result == "0 min"

    def test_very_small_distance_rounds_to_0_min(self):
        result = _travel_time_estimate(0.4)
        assert result == "0 min"


class TestCandidateRisk:
    def test_returns_string(self):
        candidate = {"id": 99, "category": "beach"}
        risk = _candidate_risk(candidate, "2026-07-01", "2026-07-03")
        assert risk in ("green", "yellow", "red")

    def test_always_green_or_yellow_no_storms(self):
        for dest_id in range(1, 50, 7):
            candidate = {"id": dest_id, "category": "city"}
            risk = _candidate_risk(candidate, "2026-07-01", "2026-07-03")
            assert risk in ("green", "yellow"), f"id={dest_id} got {risk}"

    def test_deterministic_with_seed(self):
        candidate = {"id": 42, "category": "beach"}
        r1 = _candidate_risk(candidate, "2026-08-01", "2026-08-05")
        r2 = _candidate_risk(candidate, "2026-08-01", "2026-08-05")
        assert r1 == r2

    def test_single_date(self):
        candidate = {"id": 7, "category": "mountain"}
        risk = _candidate_risk(candidate, "2026-09-01", "2026-09-01")
        assert risk in ("green", "yellow")

    def test_long_date_range(self):
        candidate = {"id": 15, "category": "city"}
        risk = _candidate_risk(candidate, "2026-10-01", "2026-10-14")
        assert risk in ("green", "yellow", "red")


class TestFindAlternatives:
    def test_luzon_destination_returns_luzon_alternatives(self):
        result = find_alternatives(1, "El Nido", 11.1958, 119.4092, "MIMAROPA")
        assert result["island_group"] == "Luzon"
        assert len(result["alternatives"]) >= 1
        for alt in result["alternatives"]:
            assert alt.risk_level in ("green", "yellow")
            assert alt.distance_km > 0

    def test_visayas_destination_returns_visayas_alternatives(self):
        result = find_alternatives(2, "Boracay", 11.9674, 121.9248, "Western Visayas")
        assert result["island_group"] == "Visayas"
        assert len(result["alternatives"]) >= 1

    def test_mindanao_destination(self):
        result = find_alternatives(13, "Davao City", 7.1907, 125.4553, "Davao")
        assert result["island_group"] == "Mindanao"
        assert len(result["alternatives"]) >= 1

    def test_unknown_region_returns_zero_alternatives(self):
        result = find_alternatives(1, "Nowhere", 0, 0, "Unknown Region")
        assert result["total_found"] == 0
        assert result["note"] == "Island group not determined for this destination."

    def test_limited_to_max_3(self):
        result = find_alternatives(1, "El Nido", 11.1958, 119.4092, "MIMAROPA")
        assert len(result["alternatives"]) <= 3

    def test_sorted_by_distance(self):
        result = find_alternatives(1, "El Nido", 11.1958, 119.4092, "MIMAROPA")
        distances = [a.distance_km for a in result["alternatives"]]
        assert distances == sorted(distances)

    def test_origin_not_in_results(self):
        result = find_alternatives(1, "El Nido", 11.1958, 119.4092, "MIMAROPA")
        for alt in result["alternatives"]:
            assert alt.destination.id != 1

    def test_note_when_fewer_than_3(self):
        result = find_alternatives(5, "Puerto Princesa", 9.7397, 118.7353, "MIMAROPA")
        if result["total_found"] < result["requested"] and result["total_found"] > 0:
            assert result["note"] is not None
            assert "found" in result["note"]
