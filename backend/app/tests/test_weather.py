import pytest

from app.services.weather import (
    _safe_float,
    _compute_dates,
    _match_area,
    _parse_temp_c,
    _map_pagasa_condition,
    _parse_fiveday,
)


class TestSafeFloat:
    def test_none_returns_zero(self):
        assert _safe_float(None) == 0.0

    def test_int_returns_float(self):
        assert _safe_float(42) == 42.0

    def test_float_returns_unchanged(self):
        assert _safe_float(3.14) == 3.14

    def test_numeric_string_returns_float(self):
        assert _safe_float("25.5") == 25.5

    def test_invalid_string_returns_zero(self):
        assert _safe_float("abc") == 0.0

    def test_empty_dict_returns_zero(self):
        assert _safe_float({}) == 0.0


class TestComputeDates:
    def test_both_dates_given(self):
        result = _compute_dates("2026-06-01", "2026-06-03")
        assert result == ["2026-06-01", "2026-06-02", "2026-06-03"]

    def test_single_date(self):
        result = _compute_dates("2026-07-15", "2026-07-15")
        assert result == ["2026-07-15"]

    def test_end_before_start_flips(self):
        result = _compute_dates("2026-08-10", "2026-08-05")
        assert result == ["2026-08-10"]

    def test_no_dates_defaults_to_7_days(self):
        result = _compute_dates(None, None)
        assert len(result) == 7

    def test_only_start_given(self):
        result = _compute_dates("2026-09-01", None)
        assert len(result) == 7
        assert result[0] == "2026-09-01"

    def test_only_end_given_defaults_start_to_today(self):
        result = _compute_dates(None, None)
        assert len(result) == 7


class TestMatchArea:
    def test_exact_match(self):
        assert _match_area("el nido", "el nido") == 1.0

    def test_substring_in_dest(self):
        assert _match_area("nido", "el nido") == 0.8

    def test_substring_in_area(self):
        assert _match_area("el nido palawan", "el nido") == 0.8

    def test_partial_word_overlap(self):
        score = _match_area("puerto princesa", "puerto galera")
        assert 0.4 <= score < 0.8

    def test_no_overlap(self):
        assert _match_area("manila", "cebu") == 0.0

    def test_both_empty_returns_1(self):
        assert _match_area("", "") == 1.0

    def test_dest_empty_area_in_dest_returns_08(self):
        assert _match_area("boracay", "") == 0.8


class TestParseTempC:
    def test_numeric_string(self):
        assert _parse_temp_c("32") == 32.0

    def test_with_degree_symbol(self):
        assert _parse_temp_c("27 °C") == 27.0

    def test_range_string_returns_zero(self):
        assert _parse_temp_c("25-30") == 0.0

    def test_negative_value(self):
        assert _parse_temp_c("-5") == -5.0

    def test_empty_string(self):
        assert _parse_temp_c("") == 0.0

    def test_non_numeric_returns_zero(self):
        assert _parse_temp_c("abc") == 0.0


class TestMapPagasaCondition:
    def test_thunderstorm_detected(self):
        assert _map_pagasa_condition("Thunderstorms") == "Thunderstorm"

    def test_storm_keyword(self):
        assert _map_pagasa_condition("Storm warning") == "Thunderstorm"

    def test_heavy_rain_maps_to_rain(self):
        assert _map_pagasa_condition("Heavy rain") == "Rain"

    def test_moderate_rain_maps_to_rain(self):
        assert _map_pagasa_condition("Moderate rain") == "Rain"

    def test_light_rain_maps_to_drizzle(self):
        assert _map_pagasa_condition("Light rain") == "Drizzle"

    def test_shower_maps_to_drizzle(self):
        assert _map_pagasa_condition("Shower") == "Drizzle"

    def test_drizzle_detected(self):
        assert _map_pagasa_condition("Drizzle") == "Drizzle"

    def test_cloudy(self):
        assert _map_pagasa_condition("Cloudy skies") == "Clouds"

    def test_overcast(self):
        assert _map_pagasa_condition("Overcast") == "Clouds"

    def test_clear(self):
        assert _map_pagasa_condition("Clear skies") == "Clear"

    def test_sunny(self):
        assert _map_pagasa_condition("Sunny") == "Clear"

    def test_fair(self):
        assert _map_pagasa_condition("Fair weather") == "Clear"

    def test_unknown_defaults_to_clouds(self):
        assert _map_pagasa_condition("Hazy") == "Clouds"

    def test_empty_string_defaults_to_clouds(self):
        assert _map_pagasa_condition("") == "Clouds"


class TestParseFiveday:
    def test_no_list_key_returns_none(self):
        assert _parse_fiveday({}, "2026-06-01", "2026-06-01") is None

    def test_empty_list_returns_none(self):
        assert _parse_fiveday({"list": []}, "2026-06-01", "2026-06-01") is None

    def test_non_list_value_returns_none(self):
        assert _parse_fiveday({"list": "not_a_list"}, "2026-06-01", "2026-06-01") is None

    def test_fallback_data_key(self):
        data = {
            "data": [
                {
                    "dt": 1800000000,
                    "main": {"temp": 30, "temp_min": 28, "temp_max": 32, "feels_like": 31, "humidity": 75},
                    "weather": [{"main": "Clear", "description": "clear sky"}],
                    "wind": {"speed": 3.5},
                    "pop": 0.1,
                }
            ]
        }
        result = _parse_fiveday(data, "2027-01-15", "2027-01-15")
        assert result is not None
        assert len(result) == 1
        assert result[0]["condition"] == "Clear"

    def test_aggregates_multiple_entries_per_day(self):
        dt = int(1800000000)
        data = {
            "list": [
                {"dt": dt, "main": {"temp": 30, "temp_min": 28, "temp_max": 32, "feels_like": 31, "humidity": 75},
                 "weather": [{"main": "Clear", "description": "clear sky"}], "wind": {"speed": 3}, "pop": 0.1},
                {"dt": dt + 3600, "main": {"temp": 32, "temp_min": 28, "temp_max": 33, "feels_like": 33, "humidity": 70},
                 "weather": [{"main": "Clouds", "description": "scattered clouds"}], "wind": {"speed": 5}, "pop": 0.2},
            ]
        }
        result = _parse_fiveday(data, "2027-01-15", "2027-01-15")
        assert result is not None
        assert result[0]["temp_max"] == 33
        assert result[0]["temp_min"] == 28
        assert result[0]["wind_speed_max"] == 5
        assert result[0]["pop_max"] == 0.2

    def test_handles_string_dt_txt(self):
        data = {
            "list": [
                {
                    "dt_txt": "2027-06-01 12:00:00",
                    "main": {"temp": 30, "temp_min": 28, "temp_max": 32, "feels_like": 31, "humidity": 75},
                    "weather": [{"main": "Rain", "description": "light rain"}],
                    "wind": {"speed": 4.0},
                    "rain": {"3h": 5.0},
                    "pop": 0.6,
                }
            ]
        }
        result = _parse_fiveday(data, "2027-06-01", "2027-06-01")
        assert result is not None
        assert result[0]["condition"] == "Rain"
        assert result[0]["rain_total_3h"] == 5.0

    def test_filters_to_requested_date_range(self):
        data = {
            "list": [
                {"dt": 1800000000, "main": {"temp": 30, "temp_min": 28, "temp_max": 32, "feels_like": 31, "humidity": 75},
                 "weather": [{"main": "Clear", "description": "clear sky"}], "wind": {"speed": 3}, "pop": 0.1},
                {"dt": 1800086400, "main": {"temp": 28, "temp_min": 26, "temp_max": 30, "feels_like": 29, "humidity": 80},
                 "weather": [{"main": "Rain", "description": "moderate rain"}], "wind": {"speed": 8}, "pop": 0.8},
            ]
        }
        result = _parse_fiveday(data, "2027-01-15", "2027-01-15")
        assert result is not None
        assert len(result) == 1
