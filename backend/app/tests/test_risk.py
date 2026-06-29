import pytest
from app.services.risk import calculate_daily_risk, get_storm_signal, get_overall_trip_risk, risk_level_to_badge


def make_day(wind_max_ms: float = 0, rain_mm: float = 0, pop: float = 0, condition: str = "Clear", category: str = "beach"):
    return {
        "wind_speed_max": wind_max_ms,
        "rain_total_3h": rain_mm,
        "pop_max": pop,
        "condition": condition,
        "category": category,
    }


HISTORICAL_STORM_TESTS = [
    {
        "name": "Typhoon Haiyan (Yolanda) — Signal No. 5",
        "day": make_day(wind_max_ms=85.0, rain_mm=80.0, pop=1.0, condition="Thunderstorm"),
        "expected_signal": 5,
        "expected_risk": "red",
        "desc": "Super typhoon with extreme winds >220 km/h",
    },
    {
        "name": "Typhoon Rai (Odette) — Signal No. 5",
        "day": make_day(wind_max_ms=70.0, rain_mm=90.0, pop=0.95, condition="Thunderstorm"),
        "expected_signal": 5,
        "expected_risk": "red",
        "desc": "Super typhoon with extreme winds and heavy rain",
    },
    {
        "name": "Typhoon Mangkhut (Ompong) — Signal No. 4",
        "day": make_day(wind_max_ms=55.0, rain_mm=65.0, pop=0.9, condition="Thunderstorm"),
        "expected_signal": 4,
        "expected_risk": "red",
        "desc": "Typhoon with very destructive winds",
    },
    {
        "name": "Typhoon Goni (Rolly) — Signal No. 5",
        "day": make_day(wind_max_ms=95.0, rain_mm=100.0, pop=0.98, condition="Thunderstorm"),
        "expected_signal": 5,
        "expected_risk": "red",
        "desc": "Most powerful typhoon to make landfall in history",
    },
    {
        "name": "Typhoon Vamco (Ulysses) — Signal No. 4",
        "day": make_day(wind_max_ms=50.0, rain_mm=120.0, pop=0.95, condition="Rain"),
        "expected_signal": 4,
        "expected_risk": "red",
        "desc": "Typhoon with extreme flooding rainfall",
    },
    {
        "name": "Typhoon Molave (Quinta) — Signal No. 3",
        "day": make_day(wind_max_ms=37.0, rain_mm=45.0, pop=0.8, condition="Rain"),
        "expected_signal": 3,
        "expected_risk": "red",
        "desc": "Typhoon with destructive winds",
    },
    {
        "name": "Tropical Storm Megi (Agaton) — Signal No. 2",
        "day": make_day(wind_max_ms=20.0, rain_mm=60.0, pop=0.85, condition="Rain"),
        "expected_signal": 2,
        "expected_risk": "red",
        "desc": "Tropical storm with heavy rainfall causing landslides",
    },
    {
        "name": "Typhoon Noru (Karding) — Signal No. 5",
        "day": make_day(wind_max_ms=78.0, rain_mm=55.0, pop=0.9, condition="Thunderstorm"),
        "expected_signal": 5,
        "expected_risk": "red",
        "desc": "Super typhoon with rapid intensification",
    },
    {
        "name": "Tropical Depression 01W — Signal No. 1",
        "day": make_day(wind_max_ms=9.5, rain_mm=30.0, pop=0.7, condition="Rain"),
        "expected_signal": 1,
        "expected_risk": "red",
        "desc": "Low-end tropical depression, minimal storm signal",
    },
    {
        "name": "Fair weather day — No Signal",
        "day": make_day(wind_max_ms=4.0, rain_mm=0.0, pop=0.1, condition="Clear", category="city"),
        "expected_signal": 0,
        "expected_risk": "green",
        "desc": "Clear skies, calm winds, no weather concerns",
    },
]


class TestStormSignal:
    def test_all_historical_storms_meet_red_threshold(self):
        failures = []
        for tc in HISTORICAL_STORM_TESTS:
            signal = get_storm_signal(tc["day"]["wind_speed_max"], tc["day"]["rain_total_3h"])
            risk, _ = calculate_daily_risk(tc["day"])
            if tc["expected_signal"] >= 1 and risk != "red":
                failures.append(f"{tc['name']}: expected red but got {risk}")
        assert not failures, "\n".join(failures)

    @pytest.mark.parametrize("tc", HISTORICAL_STORM_TESTS, ids=lambda t: t["name"])
    def test_individual_storm(self, tc):
        signal = get_storm_signal(tc["day"]["wind_speed_max"], tc["day"]["rain_total_3h"])
        risk, _ = calculate_daily_risk(tc["day"])

        assert signal == tc["expected_signal"], f"Signal mismatch for {tc['name']}: got {signal}, expected {tc['expected_signal']}"
        assert risk == tc["expected_risk"], f"Risk mismatch for {tc['name']}: got {risk}, expected {tc['expected_risk']}"


class TestEdgeCases:
    def test_signal_no1_boundary_low_side(self):
        day = make_day(wind_max_ms=8.2, rain_mm=0)
        signal = get_storm_signal(day["wind_speed_max"])
        risk, _ = calculate_daily_risk(day)
        assert signal == 0
        assert risk != "red"

    def test_signal_no1_boundary_high_side(self):
        day = make_day(wind_max_ms=8.4, rain_mm=30)
        signal = get_storm_signal(day["wind_speed_max"], day["rain_total_3h"])
        risk, _ = calculate_daily_risk(day)
        assert signal >= 1
        assert risk == "red"

    def test_rain_above_50_is_red(self):
        day = make_day(wind_max_ms=2, rain_mm=55)
        risk, _ = calculate_daily_risk(day)
        assert risk == "red"

    def test_moderate_rain_is_yellow(self):
        day = make_day(wind_max_ms=2, rain_mm=25)
        risk, _ = calculate_daily_risk(day)
        assert risk == "yellow"

    def test_thunderstorm_is_red(self):
        day = make_day(wind_max_ms=5, rain_mm=10, condition="Thunderstorm")
        risk, _ = calculate_daily_risk(day)
        assert risk == "red"

    def test_calm_clear_is_green(self):
        day = make_day(wind_max_ms=2, rain_mm=0, pop=0, condition="Clear", category="city")
        risk, _ = calculate_daily_risk(day)
        assert risk == "green"

    def test_coastal_destination_mentions_sea(self):
        day = make_day(wind_max_ms=10, rain_mm=5, category="beach")
        risk, reason = calculate_daily_risk(day)
        assert risk == "yellow"
        assert "sea" in reason.lower() or "coastal" in reason.lower()

    def test_missing_keys_default_to_zero(self):
        day = {}
        risk, reason = calculate_daily_risk(day)
        assert risk == "green"
        assert reason == "Fair weather, good for travel"

    def test_zero_values_return_green(self):
        day = make_day(wind_max_ms=0, rain_mm=0, pop=0, condition="", category="city")
        risk, _ = calculate_daily_risk(day)
        assert risk == "green"

    def test_just_above_rain_threshold_returns_red(self):
        day = make_day(wind_max_ms=2, rain_mm=50.1, pop=0.5, category="city")
        risk, _ = calculate_daily_risk(day)
        assert risk == "red"

    def test_rain_plus_high_pop_at_threshold(self):
        day = make_day(wind_max_ms=2, rain_mm=30.1, pop=0.71, category="city")
        risk, _ = calculate_daily_risk(day)
        assert risk == "red"

    def test_rain_below_threshold_with_high_pop_is_yellow(self):
        day = make_day(wind_max_ms=2, rain_mm=20.1, pop=0.8, category="city")
        risk, _ = calculate_daily_risk(day)
        assert risk == "yellow"

    def test_non_coastal_does_not_mention_sea(self):
        day = make_day(wind_max_ms=10, rain_mm=5, category="city")
        risk, reason = calculate_daily_risk(day)
        assert risk == "yellow"
        assert "sea" not in reason.lower()

    def test_island_category_is_coastal(self):
        day = make_day(wind_max_ms=10, rain_mm=5, category="island")
        risk, reason = calculate_daily_risk(day)
        assert risk == "yellow"
        assert "sea" in reason.lower() or "coastal" in reason.lower()


class TestGetStormSignal:
    def test_no_wind_returns_zero(self):
        assert get_storm_signal(0, 0) == 0

    def test_wind_below_threshold_returns_zero(self):
        assert get_storm_signal(8.0, 30) == 0

    def test_wind_above_threshold_but_no_rain_returns_zero(self):
        assert get_storm_signal(20, 0) == 0

    def test_wind_and_rain_meet_signal_no1(self):
        assert get_storm_signal(9, 15) >= 1

    def test_wind_and_rain_meet_signal_no2(self):
        assert get_storm_signal(18, 15) >= 2

    def test_wind_and_rain_meet_signal_no3(self):
        assert get_storm_signal(35, 15) >= 3

    def test_wind_and_rain_meet_signal_no4(self):
        assert get_storm_signal(50, 15) >= 4

    def test_wind_and_rain_meet_signal_no5(self):
        assert get_storm_signal(62, 15) >= 5

    def test_exact_threshold_boundary(self):
        assert get_storm_signal(30 / 3.6, 15) >= 1

    def test_rain_just_below_15_returns_zero(self):
        assert get_storm_signal(62, 14.9) == 0

    def test_negative_wind_returns_zero(self):
        assert get_storm_signal(-5, 30) == 0


class TestGetOverallTripRisk:
    def test_all_green(self):
        forecasts = [
            {"risk_level": "green", "risk_reason": "Good", "day_name": "Monday"},
            {"risk_level": "green", "risk_reason": "Good", "day_name": "Tuesday"},
        ]
        level, reason = get_overall_trip_risk(forecasts)
        assert level == "green"

    def test_any_red_overrides(self):
        forecasts = [
            {"risk_level": "green", "risk_reason": "Good", "day_name": "Monday"},
            {"risk_level": "red", "risk_reason": "Storm", "day_name": "Tuesday"},
        ]
        level, reason = get_overall_trip_risk(forecasts)
        assert level == "red"
        assert "Storm" in reason

    def test_yellow_when_no_red(self):
        forecasts = [
            {"risk_level": "green", "risk_reason": "Good", "day_name": "Monday"},
            {"risk_level": "yellow", "risk_reason": "Windy", "day_name": "Tuesday"},
        ]
        level, reason = get_overall_trip_risk(forecasts)
        assert level == "yellow"

    def test_empty_list_defaults_to_green(self):
        level, reason = get_overall_trip_risk([])
        assert level == "green"

    def test_missing_keys_default_to_green(self):
        level, reason = get_overall_trip_risk([{"risk_level": "green"}])
        assert level == "green"

    def test_caps_reasons_at_3(self):
        forecasts = [
            {"risk_level": "red", "risk_reason": "A", "day_name": "Monday"},
            {"risk_level": "red", "risk_reason": "B", "day_name": "Tuesday"},
            {"risk_level": "red", "risk_reason": "C", "day_name": "Wednesday"},
            {"risk_level": "red", "risk_reason": "D", "day_name": "Thursday"},
        ]
        level, reason = get_overall_trip_risk(forecasts)
        assert level == "red"
        assert reason.count(";") == 2


class TestRiskLevelToBadge:
    def test_green(self):
        assert risk_level_to_badge("green") == {"label": "Safe", "color": "green"}

    def test_yellow(self):
        assert risk_level_to_badge("yellow") == {"label": "Caution", "color": "yellow"}

    def test_red(self):
        assert risk_level_to_badge("red") == {"label": "Avoid", "color": "red"}

    def test_unknown_level_defaults_to_yellow(self):
        assert risk_level_to_badge("purple") == {"label": "Caution", "color": "yellow"}

    def test_empty_string_defaults_to_yellow(self):
        assert risk_level_to_badge("") == {"label": "Caution", "color": "yellow"}
