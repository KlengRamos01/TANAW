from pydantic import BaseModel


class Destination(BaseModel):
    id: int
    name: str
    municipality: str
    province: str
    region: str
    latitude: float
    longitude: float
    category: str


class AlternativeDestination(BaseModel):
    destination: Destination
    distance_km: float
    travel_time_estimate: str
    risk_level: str


class AlternativesResponse(BaseModel):
    origin_id: int
    origin_name: str
    island_group: str
    alternatives: list[AlternativeDestination]
    total_found: int
    requested: int
    note: str | None = None


class DailyForecast(BaseModel):
    date: str
    day_name: str
    risk_level: str
    risk_reason: str
    summary: str


class OverallTripRisk(BaseModel):
    level: str
    label: str
    color: str
    reason: str


class ForecastResponse(BaseModel):
    destination: Destination
    forecasts: list[DailyForecast]
    overall_trip_risk: OverallTripRisk
    data_source: str
    generated_at: str


class SearchResult(BaseModel):
    destinations: list[Destination]
