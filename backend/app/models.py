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


class DailyForecast(BaseModel):
    date: str
    day_name: str
    risk_level: str
    summary: str


class ForecastResponse(BaseModel):
    destination: Destination
    forecasts: list[DailyForecast]
    data_source: str
    generated_at: str


class SearchResult(BaseModel):
    destinations: list[Destination]
