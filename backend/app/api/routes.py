from datetime import datetime, date

from fastapi import APIRouter, HTTPException, Query

from app.data.destinations import TOP_50_DESTINATIONS
from app.models import Destination, DailyForecast, OverallTripRisk, ForecastResponse, SearchResult, AlternativesResponse
from app.services.alternatives import find_alternatives
from app.services.gemini import generate_summaries
from app.services.risk import calculate_daily_risk, get_overall_trip_risk, risk_level_to_badge
from app.services.validation import (
    sanitize_string,
    validate_search_query,
    validate_destination_name,
    validate_date,
    validate_latitude,
    validate_longitude,
    validate_destination_id,
)
from app.services.weather import fetch_forecast, lookup_city

router = APIRouter(prefix="/api", tags=["forecast"])

_next_virtual_id = 1000


def _next_id() -> int:
    global _next_virtual_id
    _next_virtual_id += 1
    return _next_virtual_id - 1


@router.get("/destinations/search", response_model=SearchResult)
async def search_destinations(query: str = Query(..., min_length=1)):
    try:
        q = validate_search_query(query)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    q_lower = q.lower()
    matches = [
        Destination(**d)
        for d in TOP_50_DESTINATIONS
        if q_lower in d["name"].lower() or q_lower in d["province"].lower() or q_lower in d["municipality"].lower()
    ]

    return SearchResult(destinations=matches[:10])


@router.get("/forecast", response_model=ForecastResponse)
async def get_destination_forecast(
    destination_id: int = Query(None, description="Pre-loaded destination ID"),
    destination_name: str = Query(None, description="Any location name"),
    start_date: str = Query(None, description="Trip start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Trip end date (YYYY-MM-DD)"),
):
    if destination_id is None and not destination_name:
        raise HTTPException(status_code=400, detail="Provide destination_id or destination_name.")

    dest_id = None
    try:
        dest_id = validate_destination_id(destination_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    s_date = None
    e_date = None
    try:
        s_date = validate_date(start_date)
        e_date = validate_date(end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    dest_name_safe = validate_destination_name(destination_name)

    destination = None

    if dest_id:
        dest_data = next((d for d in TOP_50_DESTINATIONS if d["id"] == dest_id), None)
        if dest_data:
            destination = Destination(**dest_data)

    if not destination and dest_name_safe:
        dest_data = next(
            (d for d in TOP_50_DESTINATIONS if d["name"].lower() == dest_name_safe.lower()),
            None,
        )
        if dest_data:
            destination = Destination(**dest_data)
        else:
            city = await lookup_city(dest_name_safe)
            if city:
                destination = Destination(
                    id=_next_id(),
                    name=sanitize_string(city["name"]),
                    municipality=sanitize_string(city["name"]),
                    province=sanitize_string(city.get("country", "")),
                    region="",
                    latitude=city["lat"],
                    longitude=city["lon"],
                    category="city",
                )

    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found. Try searching a different name.")

    daily_weather = await fetch_forecast(destination.name, destination.latitude, destination.longitude, s_date, e_date)

    if not daily_weather:
        raise HTTPException(status_code=503, detail="Weather data unavailable from all sources. Try again later.")

    enriched = []
    for dw in daily_weather:
        dw["category"] = destination.category
        risk_level, risk_reason = calculate_daily_risk(dw)

        try:
            dt = datetime.strptime(dw["date"], "%Y-%m-%d")
            day_name = dt.strftime("%A")
        except ValueError:
            day_name = ""

        enriched.append({
            "date": dw["date"],
            "day_name": day_name,
            "risk_level": risk_level,
            "risk_reason": risk_reason,
            "wind_speed_max": dw.get("wind_speed_max", 0),
            "rain_total_3h": dw.get("rain_total_3h", 0),
            "condition": dw.get("condition", ""),
            "description": dw.get("description", ""),
            "pop_max": dw.get("pop_max", 0),
        })

    summaries = await generate_summaries(enriched, destination.name)

    forecasts = []
    for i, f in enumerate(enriched):
        forecasts.append(DailyForecast(
            date=f["date"],
            day_name=f["day_name"],
            risk_level=f["risk_level"],
            risk_reason=f["risk_reason"],
            summary=summaries[i] if i < len(summaries) else "",
        ))

    overall_level, overall_reason = get_overall_trip_risk([f.model_dump() for f in forecasts])

    return ForecastResponse(
        destination=destination,
        forecasts=forecasts,
        overall_trip_risk=OverallTripRisk(
            level=overall_level,
            **risk_level_to_badge(overall_level),
            reason=overall_reason,
        ),
        data_source="OpenWeatherMap / PAGASA / Gemini",
        generated_at=datetime.utcnow().isoformat() + "Z",
    )


@router.get("/alternatives", response_model=AlternativesResponse)
async def get_alternatives(
    destination_id: int = Query(..., description="Pre-loaded destination ID"),
    destination_name: str = Query(None, description="Origin name"),
    lat: float = Query(None, description="Origin latitude"),
    lon: float = Query(None, description="Origin longitude"),
    region: str = Query("", description="Origin region"),
    start_date: str = Query(None, description="Trip start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Trip end date (YYYY-MM-DD)"),
):
    try:
        validate_destination_id(destination_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        s_date = validate_date(start_date)
        e_date = validate_date(end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    dest_data = next((d for d in TOP_50_DESTINATIONS if d["id"] == destination_id), None)
    if not dest_data:
        return AlternativesResponse(
            origin_id=destination_id,
            origin_name=sanitize_string(destination_name or ""),
            island_group="",
            alternatives=[],
            total_found=0,
            requested=3,
            note="Alternatives are available only for pre-loaded destinations.",
        )

    result = find_alternatives(
        destination_id=dest_data["id"],
        destination_name=dest_data["name"],
        lat=dest_data["latitude"],
        lon=dest_data["longitude"],
        region=dest_data["region"],
        start_date=s_date,
        end_date=e_date,
    )
    return AlternativesResponse(**result)
