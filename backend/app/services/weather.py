import random
from collections import Counter, defaultdict
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


async def fetch_forecast(dest_name: str, lat: float, lon: float) -> list[dict]:
    if not settings.weather_api_key:
        return _generate_mock_forecast()

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
                return _extrapolate_7day(data)
    except Exception:
        pass

    return _generate_mock_forecast()


def _extrapolate_7day(current: dict) -> list[dict]:
    today = datetime.now().date()

    temp_f = current["main"]["temp"]
    feels_like_f = current["main"]["feels_like"]
    humidity = current["main"]["humidity"]
    wind_mph = current["wind"]["speed"]
    weather = current["weather"][0]

    temp_c = _f_to_c(temp_f)
    feels_like_c = _f_to_c(feels_like_f)
    wind_ms = _mph_to_ms(wind_mph)

    result = []
    for i in range(7):
        date = (today + timedelta(days=i)).isoformat()

        variation = 1 + (i * 0.5 - 1.5) * 0.03 + random.uniform(-0.04, 0.04)
        day_temp = round(temp_c * variation, 1)
        day_feels = round(feels_like_c * variation, 1)
        day_humidity = max(40, min(100, humidity + random.randint(-15, 10)))
        day_wind = max(0, round(wind_ms + random.uniform(-2, 5), 1))

        if i == 0:
            cond, desc = weather["main"], weather["description"]
        else:
            idx = random.randint(0, len(CONDITIONS_POOL) - 1)
            cond, desc = CONDITIONS_POOL[idx]

        result.append({
            "date": date,
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


def _f_to_c(f: float) -> float:
    return round((f - 32) * 5 / 9, 1)


def _mph_to_ms(mph: float) -> float:
    return round(mph * 0.44704, 1)


def _generate_mock_forecast() -> list[dict]:
    random.seed(42)

    result = []
    for i in range(7):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        cond, desc = CONDITIONS_POOL[i % len(CONDITIONS_POOL)]
        result.append({
            "date": date,
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
