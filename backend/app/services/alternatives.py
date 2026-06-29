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
            "total_found": 0,
            "requested": 3,
            "note": "Island group not determined for this destination.",
        }

    candidates = [d for d in TOP_50_DESTINATIONS if d["id"] != destination_id and get_island_group(d["region"]) == island_group]

    safe_candidates = []
    for c in candidates:
        risk = _candidate_risk(c, start_date, end_date)
        if risk in ("green", "yellow"):
            dist = _haversine_km(lat, lon, c["latitude"], c["longitude"])
            safe_candidates.append((dist, c))

    safe_candidates.sort(key=lambda x: x[0])

    requested = 3
    top = safe_candidates[:requested]

    from app.models import Destination

    alternatives = []
    for dist, c in top:
        from app.models import AlternativeDestination

        risk = _candidate_risk(c, start_date, end_date)
        alternatives.append(AlternativeDestination(
            destination=Destination(**c),
            distance_km=dist,
            travel_time_estimate=_travel_time_estimate(dist),
            risk_level=risk,
        ))

    note = None
    if len(safe_candidates) < requested:
        note = f"Only {len(safe_candidates)} better-rated {'destination' if len(safe_candidates) == 1 else 'destinations'} found in {island_group}." if len(safe_candidates) > 0 else f"No green or yellow destinations found in {island_group}."

    return {
        "origin_id": destination_id,
        "origin_name": destination_name,
        "island_group": island_group,
        "alternatives": alternatives,
        "total_found": len(safe_candidates),
        "requested": requested,
        "note": note,
    }
