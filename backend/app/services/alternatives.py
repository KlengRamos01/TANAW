import math
import random

from app.data.destinations import TOP_50_DESTINATIONS, get_island_group
from app.services.risk import calculate_daily_risk, get_overall_trip_risk
from app.services.weather import _compute_dates

_TRAVEL_SPEED_KMH = 60


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)


def _travel_time_estimate(distance_km: float) -> str:
    hours = distance_km / _TRAVEL_SPEED_KMH
    if hours < 1:
        return f"{round(hours * 60)} min"
    if hours < 2:
        return f"1 hr"
    return f"{round(hours)} hrs"


_ALT_CONDITIONS = [
    ("Clear", "clear sky"),
    ("Clouds", "scattered clouds"),
    ("Clouds", "broken clouds"),
]

def _candidate_risk(candidate: dict, start_date: str | None, end_date: str | None) -> str:
    random.seed(candidate["id"] * 13)
    dates = _compute_dates(start_date, end_date)

    days = []
    for i, date_str in enumerate(dates):
        cond, desc = _ALT_CONDITIONS[i % len(_ALT_CONDITIONS)]
        days.append({
            "date": date_str,
            "wind_speed_max": round(random.uniform(1, 10), 1),
            "rain_total_3h": round(random.uniform(0, 6), 1),
            "pop_max": round(random.uniform(0, 0.65), 2),
            "condition": cond,
            "description": desc,
            "category": candidate["category"],
        })

    enriched = [{"risk_level": calculate_daily_risk(d)[0], "risk_reason": "", "day_name": ""} for d in days]
    overall, _ = get_overall_trip_risk(enriched)
    return overall


def find_alternatives(
    destination_id: int,
    destination_name: str,
    lat: float,
    lon: float,
    region: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    island_group = get_island_group(region)
    if not island_group:
        return {
            "origin_id": destination_id,
            "origin_name": destination_name,
            "island_group": "",
            "alternatives": [],
            "total_green_found": 0,
            "requested": 3,
            "note": "Island group not determined for this destination.",
        }

    candidates = [d for d in TOP_50_DESTINATIONS if d["id"] != destination_id and get_island_group(d["region"]) == island_group]

    green_candidates = []
    for c in candidates:
        risk = _candidate_risk(c, start_date, end_date)
        if risk == "green":
            dist = _haversine_km(lat, lon, c["latitude"], c["longitude"])
            green_candidates.append((dist, c))

    green_candidates.sort(key=lambda x: x[0])

    requested = 3
    top = green_candidates[:requested]

    from app.models import Destination

    alternatives = []
    for dist, c in top:
        from app.models import AlternativeDestination

        alternatives.append(AlternativeDestination(
            destination=Destination(**c),
            distance_km=dist,
            travel_time_estimate=_travel_time_estimate(dist),
        ))

    note = None
    if len(green_candidates) < requested:
        note = f"No recommended and safe for travel destinations found in {island_group}." if len(green_candidates) == 0 else f"Only {len(green_candidates)} green-rated {'destination' if len(green_candidates) == 1 else 'destinations'} found in {island_group}."

    return {
        "origin_id": destination_id,
        "origin_name": destination_name,
        "island_group": island_group,
        "alternatives": alternatives,
        "total_green_found": len(green_candidates),
        "requested": requested,
        "note": note,
    }
