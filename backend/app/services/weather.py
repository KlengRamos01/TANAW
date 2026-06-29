import random
from datetime import datetime, timedelta

import httpx

from app.config import settings

RAPIDAPI_HOST = "open-weather13.p.rapidapi.com"

CONDITIONS_POOL = [
    ("Clear", "clear sky"),
    ("Clear", "few clouds"),
    ("Clouds", "scattered clouds"),
    ("Clouds", "broken clouds"),
    ("Clouds", "overcast clouds"),
    ("Rain", "light rain"),
    ("Rain", "moderate rain"),
    ("Rain", "heavy intensity rain"),
    ("Thunderstorm", "thunderstorm"),
    ("Drizzle", "light intensity drizzle"),
]


async def fetch_forecast(dest_name: str, lat: float, lon: float, start_date: str | None = None, end_date: str | None = None) -> list[dict]:
    if not settings.weather_api_key:
        return _generate_range(start_date, end_date)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://{RAPIDAPI_HOST}/city",
                params={"city": dest_name, "lang": "EN"},
                headers={
                    "x-rapidapi-key": settings.weather_api_key,
                    "x-rapidapi-host": RAPIDAPI_HOST,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                return _extrapolate_range(data, start_date, end_date)
    except Exception:
        pass

    return _generate_range(start_date, end_date)


async def lookup_city(name: str) -> dict | None:
    if not settings.weather_api_key:
        return None

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://{RAPIDAPI_HOST}/city",
                params={"city": name, "lang": "EN"},
                headers={
                    "x-rapidapi-key": settings.weather_api_key,
                    "x-rapidapi-host": RAPIDAPI_HOST,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                country = data.get("sys", {}).get("country", "")
                if country != "PH":
                    return None
                return {
                    "name": data.get("name", name),
                    "lat": data["coord"]["lat"],
                    "lon": data["coord"]["lon"],
                    "country": country,
                }
    except Exception:
        pass
    return None


def _compute_dates(start_date: str | None, end_date: str | None) -> list[str]:
    today = datetime.now().date()

    if start_date:
        s = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        s = today

    if end_date:
        e = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        e = s + timedelta(days=6)

    if e < s:
        e = s

    return [(s + timedelta(days=i)).isoformat() for i in range((e - s).days + 1)]


def _extrapolate_range(current: dict, start_date: str | None, end_date: str | None) -> list[dict]:
    dates = _compute_dates(start_date, end_date)

    temp_f = current["main"]["temp"]
    feels_like_f = current["main"]["feels_like"]
    humidity = current["main"]["humidity"]
    wind_mph = current["wind"]["speed"]
    weather = current["weather"][0]

    temp_c = _f_to_c(temp_f)
    feels_like_c = _f_to_c(feels_like_f)
    wind_ms = _mph_to_ms(wind_mph)

    today = datetime.now().date()
    result = []
    for i, date_str in enumerate(dates):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        day_offset = (date_obj - today).days

        variation = 1 + (abs(day_offset) * 0.03) + random.uniform(-0.04, 0.04)
        day_temp = round(temp_c * variation, 1)
        day_feels = round(feels_like_c * variation, 1)
        day_humidity = max(40, min(100, humidity + random.randint(-15, 10)))
        day_wind = max(0, round(wind_ms + random.uniform(-2, 5), 1))

        if day_offset == 0:
            cond, desc = weather["main"], weather["description"]
        else:
            idx = random.randint(0, len(CONDITIONS_POOL) - 1)
            cond, desc = CONDITIONS_POOL[idx]

        result.append({
            "date": date_str,
            "temp_min": round(day_temp - random.uniform(2, 5), 1),
            "temp_max": round(day_temp + random.uniform(1, 4), 1),
            "temp_avg": day_temp,
            "feels_like_avg": day_feels,
            "humidity_avg": day_humidity,
            "wind_speed_max": round(day_wind * 1.5, 1),
            "wind_speed_avg": day_wind,
            "condition": cond,
            "description": desc,
            "rain_total_3h": round(random.uniform(0, 10), 1) if cond in ("Rain", "Thunderstorm", "Drizzle") else 0,
            "pop_max": round(random.uniform(0, 1), 2),
        })

    return result


def _generate_range(start_date: str | None, end_date: str | None, seed: int = 42) -> list[dict]:
    random.seed(seed)
    dates = _compute_dates(start_date, end_date)

    result = []
    for i, date_str in enumerate(dates):
        cond, desc = CONDITIONS_POOL[i % len(CONDITIONS_POOL)]
        result.append({
            "date": date_str,
            "temp_min": round(random.uniform(22, 26), 1),
            "temp_max": round(random.uniform(29, 34), 1),
            "temp_avg": round(random.uniform(26, 30), 1),
            "feels_like_avg": round(random.uniform(27, 33), 1),
            "humidity_avg": random.randint(65, 95),
            "wind_speed_max": round(random.uniform(5, 40), 1),
            "wind_speed_avg": round(random.uniform(3, 18), 1),
            "condition": cond,
            "description": desc,
            "rain_total_3h": round(random.uniform(0, 12), 1),
            "pop_max": round(random.uniform(0, 1), 2),
        })

    return result


def _f_to_c(f: float) -> float:
    return round((f - 32) * 5 / 9, 1)


def _mph_to_ms(mph: float) -> float:
    return round(mph * 0.44704, 1)
