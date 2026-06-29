PAGASA_WIND_KMH_THRESHOLDS = [
    (30, 1),
    (60, 2),
    (120, 3),
    (170, 4),
    (220, 5),
]

COASTAL_CATEGORIES = {"beach", "island"}


def get_storm_signal(wind_speed_max_ms: float, rain_mm: float = 0) -> int:
    wind_kmh = wind_speed_max_ms * 3.6
    signal = 0
    for threshold, sig in PAGASA_WIND_KMH_THRESHOLDS:
        if wind_kmh >= threshold and rain_mm >= 15:
            signal = sig
    return signal


def calculate_daily_risk(day: dict) -> tuple[str, str]:
    wind_max = day.get("wind_speed_max", 0)
    rain = day.get("rain_total_3h", 0)
    pop = day.get("pop_max", 0)
    condition = day.get("condition", "")
    category = day.get("category", "")

    signal = get_storm_signal(wind_max, rain)
    wind_kmh = wind_max * 3.6
    is_coastal = category in COASTAL_CATEGORIES

    if signal >= 1:
        return ("red", f"PAGASA Storm Signal No. {signal} — travel not advised")

    if wind_kmh > 55:
        return ("red", "Damaging winds expected, unsafe for travel")

    if rain > 50 or (rain > 30 and pop > 0.7):
        return ("red", "Heavy rainfall expected, flooding possible")

    if condition in ("Thunderstorm",):
        return ("red", "Thunderstorms expected, postpone outdoor plans")

    if wind_kmh > 30:
        return ("yellow", f"Moderate winds ({wind_kmh:.0f} km/h), caution advised{' for sea travel' if is_coastal else ''}")

    if rain > 20:
        return ("yellow", "Moderate rain expected, bring rain gear")

    if pop > 0.5:
        return ("yellow", "Scattered showers possible, prepare accordingly")

    return ("green", "Fair weather, good for travel")


def get_overall_trip_risk(daily_forecasts: list[dict]) -> tuple[str, str]:
    worst_risk = "green"
    worst_reason = "All days look good for travel."
    red_reasons = []
    yellow_reasons = []

    for f in daily_forecasts:
        level = f.get("risk_level", "green")
        reason = f.get("risk_reason", "")
        if level == "red":
            red_reasons.append(f"{f.get('day_name', '')}: {reason}")
            worst_risk = "red"
        elif level == "yellow" and worst_risk != "red":
            yellow_reasons.append(f"{f.get('day_name', '')}: {reason}")
            worst_risk = "yellow"

    if worst_risk == "red":
        return ("red", "; ".join(red_reasons[:3]))
    elif worst_risk == "yellow":
        return ("yellow", "; ".join(yellow_reasons[:3]))
    return ("green", worst_reason)


def risk_level_to_badge(level: str) -> dict:
    mapping = {
        "green": {"label": "Safe", "color": "green"},
        "yellow": {"label": "Caution", "color": "yellow"},
        "red": {"label": "Avoid", "color": "red"},
    }
    return mapping.get(level, mapping["yellow"])
