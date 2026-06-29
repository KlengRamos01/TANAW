import pytest
from app.services.risk import calculate_daily_risk, get_storm_signal


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
