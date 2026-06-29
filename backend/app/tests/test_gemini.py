import pytest

from app.services.gemini import _build_prompt, _parse_response, _fallback_summaries


class TestBuildPrompt:
    def test_includes_destination_name(self):
        forecasts = [{"day_name": "Monday", "date": "2026-06-01", "risk_level": "green",
                       "wind_speed_max": 5, "rain_total_3h": 0, "condition": "Clear", "description": "clear sky"}]
        prompt = _build_prompt(forecasts, "El Nido")
        assert "El Nido" in prompt

    def test_includes_risk_badge(self):
        forecasts = [{"day_name": "Monday", "date": "2026-06-01", "risk_level": "red",
                       "wind_speed_max": 50, "rain_total_3h": 80, "condition": "Rain", "description": "heavy rain"}]
        prompt = _build_prompt(forecasts, "Test")
        assert "RED" in prompt

    def test_multiple_days(self):
        forecasts = [
            {"day_name": "Monday", "date": "2026-06-01", "risk_level": "green",
             "wind_speed_max": 5, "rain_total_3h": 0, "condition": "Clear", "description": "clear sky"},
            {"day_name": "Tuesday", "date": "2026-06-02", "risk_level": "yellow",
             "wind_speed_max": 15, "rain_total_3h": 10, "condition": "Clouds", "description": "scattered clouds"},
        ]
        prompt = _build_prompt(forecasts, "Test")
        assert prompt.count("- ") == 2

    def test_missing_fields_uses_defaults(self):
        forecasts = [{"day_name": "Monday", "date": "2026-06-01", "risk_level": "green"}]
        prompt = _build_prompt(forecasts, "Test")
        assert "0 m/s" in prompt
        assert "0mm" in prompt


class TestParseResponse:
    def test_simple_lines(self):
        result = _parse_response("Sunny day ahead.\nRain expected later.\n", 2)
        assert len(result) == 2
        assert result[0] == "Sunny day ahead."

    def test_pipe_delimited(self):
        result = _parse_response("A|B|Wear sunscreen today.\nC|D|Bring an umbrella.\n", 2)
        assert result[0] == "Wear sunscreen today."
        assert result[1] == "Bring an umbrella."

    def test_short_lines_filtered(self):
        result = _parse_response("Hi\nThis is a proper long sentence.\nOK\n", 3)
        assert len(result) == 1

    def test_empty_text(self):
        result = _parse_response("", 3)
        assert result == []

    def test_capped_to_expected_count(self):
        text = "\n".join([f"Line {i} with enough characters to pass." for i in range(10)])
        result = _parse_response(text, 3)
        assert len(result) == 3


class TestFallbackSummaries:
    def test_green_risk_clear_condition(self):
        result = _fallback_summaries([{"risk_level": "green", "condition": "Clear"}])
        assert "Sunny" in result[0]

    def test_yellow_risk_clouds_condition(self):
        result = _fallback_summaries([{"risk_level": "yellow", "condition": "Clouds"}])
        assert "umbrella" in result[0].lower() or "cloudy" in result[0].lower()

    def test_red_risk_rain_condition(self):
        result = _fallback_summaries([{"risk_level": "red", "condition": "Rain"}])
        assert "rain" in result[0].lower()

    def test_thunderstorm_condition(self):
        result = _fallback_summaries([{"risk_level": "red", "condition": "Thunderstorm"}])
        assert "thunderstorm" in result[0].lower() or "postpone" in result[0].lower()

    def test_unknown_condition_falls_back_to_risk(self):
        result = _fallback_summaries([{"risk_level": "green", "condition": "Unknown"}])
        assert "Sunny" in result[0]

    def test_empty_daily_list(self):
        result = _fallback_summaries([])
        assert result == []

    def test_missing_condition_key(self):
        result = _fallback_summaries([{"risk_level": "green"}])
        assert "Sunny" in result[0]

    def test_multiple_days(self):
        result = _fallback_summaries([
            {"risk_level": "green", "condition": "Clear"},
            {"risk_level": "yellow", "condition": "Clouds"},
            {"risk_level": "red", "condition": "Rain"},
        ])
        assert len(result) == 3
