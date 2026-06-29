from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.data.destinations import TOP_50_DESTINATIONS
from app.models import Destination, DailyForecast, ForecastResponse, SearchResult
from app.services.gemini import generate_forecast_summaries
from app.services.weather import fetch_forecast

router = APIRouter(prefix="/api", tags=["forecast"])


@router.get("/destinations/search", response_model=SearchResult)
async def search_destinations(query: str = Query(..., min_length=1)):
    q = query.strip().lower()
    matches = [
        Destination(**d)
        for d in TOP_50_DESTINATIONS
        if q in d["name"].lower() or q in d["province"].lower() or q in d["municipality"].lower()
    ]

    if not matches:
        raise HTTPException(status_code=404, detail="No destination found. Try a different search term.")

    return SearchResult(destinations=matches[:10])


@router.get("/forecast/{destination_id}", response_model=ForecastResponse)
async def get_destination_forecast(destination_id: int):
    dest_data = next((d for d in TOP_50_DESTINATIONS if d["id"] == destination_id), None)
    if not dest_data:
        raise HTTPException(status_code=404, detail="Destination not found.")

    destination = Destination(**dest_data)
    daily_weather = await fetch_forecast(destination.name, destination.latitude, destination.longitude)
    summaries = await generate_forecast_summaries(daily_weather, destination.name)

    forecasts = []
    for sw in summaries:
        forecasts.append(DailyForecast(**sw))

    return ForecastResponse(
        destination=destination,
        forecasts=forecasts,
        data_source="PAGASA / OpenWeatherMap / Gemini",
        generated_at=datetime.utcnow().isoformat() + "Z",
    )
