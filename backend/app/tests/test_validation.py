import pytest

from app.services.validation import (
    sanitize_string,
    validate_search_query,
    validate_destination_name,
    validate_date,
    validate_latitude,
    validate_longitude,
    validate_destination_id,
)


class TestSanitizeString:
    def test_strips_html_tags(self):
        result = sanitize_string("<script>alert('xss')</script>Hello")
        assert result == "alert('xss')Hello"

    def test_trims_whitespace(self):
        assert sanitize_string("  hello  ") == "hello"

    def test_escapes_angle_brackets(self):
        assert "<" not in sanitize_string("<b>test</b>")

    def test_truncates_long_strings(self):
        long_str = "a" * 500
        result = sanitize_string(long_str, max_length=10)
        assert len(result) == 10

    def test_none_returns_empty(self):
        assert sanitize_string(None) == ""

    def test_empty_string_returns_empty(self):
        assert sanitize_string("") == ""

    def test_normal_text_passes_through(self):
        assert sanitize_string("El Nido, Palawan") == "El Nido, Palawan"


class TestValidateSearchQuery:
    def test_valid_query(self):
        assert validate_search_query("boracay") == "boracay"

    def test_strips_html_then_validates(self):
        result = validate_search_query("<b>manila</b>")
        assert "manila" in result

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="required"):
            validate_search_query("")

    def test_only_whitespace_raises(self):
        with pytest.raises(ValueError, match="required"):
            validate_search_query("   ")

    def test_truncates_long_query(self):
        long_q = "a" * 500
        result = validate_search_query(long_q)
        assert len(result) == 100


class TestValidateDestinationName:
    def test_valid_name(self):
        assert validate_destination_name("Puerto Princesa") == "Puerto Princesa"

    def test_none_returns_none(self):
        assert validate_destination_name(None) is None

    def test_empty_returns_none(self):
        assert validate_destination_name("") is None

    def test_whitespace_returns_none(self):
        assert validate_destination_name("   ") is None

    def test_sanitizes_html(self):
        result = validate_destination_name("<b>Tagaytay</b>")
        assert "Tagaytay" in result
        assert "<b>" not in result


class TestValidateDate:
    def test_valid_date(self):
        assert validate_date("2026-07-15") == "2026-07-15"

    def test_none_returns_none(self):
        assert validate_date(None) is None

    def test_empty_returns_none(self):
        assert validate_date("") is None

    def test_bad_format_raises(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date("15-07-2026")

    def test_wrong_separator_raises(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date("2026/07/15")

    def test_invalid_month_raises(self):
        with pytest.raises(ValueError, match="not a real calendar date"):
            validate_date("2026-13-01")

    def test_february_29_non_leap_raises(self):
        with pytest.raises(ValueError, match="not a real calendar date"):
            validate_date("2023-02-29")

    def test_out_of_range_past_raises(self):
        with pytest.raises(ValueError, match="out of valid range"):
            validate_date("2019-12-31")

    def test_out_of_range_future_raises(self):
        with pytest.raises(ValueError, match="out of valid range"):
            validate_date("2101-01-01")

    def test_leading_trailing_whitespace(self):
        assert validate_date("  2026-06-01  ") == "2026-06-01"

    def test_february_29_leap_year(self):
        assert validate_date("2024-02-29") == "2024-02-29"


class TestValidateLatitude:
    def test_valid_lat(self):
        assert validate_latitude(14.5) == 14.5

    def test_none_returns_none(self):
        assert validate_latitude(None) is None

    def test_negative_lat(self):
        assert validate_latitude(-45.0) == -45.0

    def test_exactly_90(self):
        assert validate_latitude(90.0) == 90.0

    def test_exactly_negative_90(self):
        assert validate_latitude(-90.0) == -90.0

    def test_above_90_raises(self):
        with pytest.raises(ValueError, match="out of range"):
            validate_latitude(91.0)

    def test_below_negative_90_raises(self):
        with pytest.raises(ValueError, match="out of range"):
            validate_latitude(-91.0)


class TestValidateLongitude:
    def test_valid_lon(self):
        assert validate_longitude(120.0) == 120.0

    def test_none_returns_none(self):
        assert validate_longitude(None) is None

    def test_negative_lon(self):
        assert validate_longitude(-75.0) == -75.0

    def test_exactly_180(self):
        assert validate_longitude(180.0) == 180.0

    def test_exactly_negative_180(self):
        assert validate_longitude(-180.0) == -180.0

    def test_above_180_raises(self):
        with pytest.raises(ValueError, match="out of range"):
            validate_longitude(181.0)

    def test_below_negative_180_raises(self):
        with pytest.raises(ValueError, match="out of range"):
            validate_longitude(-181.0)


class TestValidateDestinationId:
    def test_valid_id(self):
        assert validate_destination_id(5) == 5

    def test_none_returns_none(self):
        assert validate_destination_id(None) is None

    def test_zero_raises(self):
        with pytest.raises(ValueError, match="positive integer"):
            validate_destination_id(0)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="positive integer"):
            validate_destination_id(-1)
