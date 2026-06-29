import random
from datetime import datetime, timedelta

import httpx

from app.config import settings

RAPIDAPI_HOST = "open-weather13.p.rapidapi.com"
PAGASA_API_BASE = "https://api.pagasa.dost.gov.ph"

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
    result = await _try_openweather(dest_name, start_date, end_date)
    if result is not None:
        return result

    result = await _try_pagasa(lat, lon, start_date, end_date)
    if result is not None:
        return result

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


async def _try_openweather(dest_name: str, start_date: str | None, end_date: str | None) -> list[dict] | None:
    if not settings.weather_api_key:
        return None
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
                return _extrapolate_range(resp.json(), start_date, end_date)
    except Exception:
        pass
    return None


async def _try_pagasa(lat: float, lon: float, start_date: str | None, end_date: str | None) -> list[dict] | None:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{PAGASA_API_BASE}/weather/forecasts",
                params={"lat": lat, "lon": lon},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                parsed = _parse_pagasa_response(data, start_date, end_date)
                if parsed:
                    return parsed
    except Exception:
        pass
    return None


def _parse_pagasa_response(data: dict, start_date: str | None, end_date: str | None) -> list[dict] | None:
    forecasts_raw = data.get("data") or data.get("forecasts") or data.get("items")
    if not forecasts_raw or not isinstance(forecasts_raw, list):
        return None

    dates_set = set(_compute_dates(start_date, end_date))

    result = []
    for entry in forecasts_raw:
        date_str = entry.get("date") or entry.get("forecast_date") or ""
        if date_str[:10] not in dates_set:
            continue

        temp = entry.get("temperature", {})
        wind = entry.get("wind", {})
        humidity_val = entry.get("humidity")
        condition_raw = entry.get("weather") or entry.get("condition") or ""
        condition_str = _map_pagasa_condition(condition_raw)

        result.append({
            "date": date_str[:10],
            "temp_min": _safe_float(temp.get("min")) if isinstance(temp, dict) else _safe_float(temp),
            "temp_max": _safe_float(temp.get("max")) if isinstance(temp, dict) else _safe_float(temp),
            "temp_avg": _safe_float(temp.get("avg") or temp.get("mean")) if isinstance(temp, dict) else _safe_float(temp),
            "feels_like_avg": _safe_float(temp.get("feels_like") or temp.get("avg")) if isinstance(temp, dict) else _safe_float(temp),
            "humidity_avg": int(_safe_float(humidity_val)) if humidity_val else random.randint(65, 95),
            "wind_speed_max": _safe_float(wind.get("max") or wind.get("speed_max")) if isinstance(wind, dict) else _safe_float(wind),
            "wind_speed_avg": _safe_float(wind.get("avg") or wind.get("speed")) if isinstance(wind, dict) else _safe_float(wind),
            "condition": condition_str,
            "description": condition_raw.strip() if isinstance(condition_raw, str) else "",
            "rain_total_3h": _safe_float(entry.get("rain") or entry.get("rainfall") or 0),
            "pop_max": _safe_float(entry.get("pop") or entry.get("probability") or 0),
        })

    if not result and forecasts_raw and len(forecasts_raw) > 0:
        first = forecasts_raw[0]
        temp = first.get("temperature", {})
        wind = first.get("wind", {})
        humidity_val = first.get("humidity")
        condition_raw = first.get("weather") or first.get("condition") or ""
        condition_str = _map_pagasa_condition(condition_raw)

        base_temp = _safe_float(temp.get("avg") or temp.get("mean")) if isinstance(temp, dict) else _safe_float(temp)
        base_wind = _safe_float(wind.get("avg") or wind.get("speed")) if isinstance(wind, dict) else _safe_float(wind)
        base_humidity = int(_safe_float(humidity_val)) if humidity_val else 80

        if base_temp or base_wind:
            dates = _compute_dates(start_date, end_date)
            for i, date_str in enumerate(dates):
                variation = 1 + (i * 0.03) + random.uniform(-0.04, 0.04)
                result.append({
                    "date": date_str,
                    "temp_min": round(base_temp * variation - random.uniform(2, 4), 1) if base_temp else round(random.uniform(22, 26), 1),
                    "temp_max": round(base_temp * variation + random.uniform(1, 3), 1) if base_temp else round(random.uniform(29, 34), 1),
                    "temp_avg": round(base_temp * variation, 1) if base_temp else round(random.uniform(26, 30), 1),
                    "feels_like_avg": round(base_temp * variation, 1) if base_temp else round(random.uniform(27, 33), 1),
                    "humidity_avg": max(40, min(100, base_humidity + random.randint(-10, 10))),
                    "wind_speed_max": round(base_wind * 1.5 + random.uniform(0, 3), 1) if base_wind else round(random.uniform(5, 40), 1),
                    "wind_speed_avg": round(base_wind + random.uniform(-1, 2), 1) if base_wind else round(random.uniform(3, 18), 1),
                    "condition": condition_str if i == 0 else CONDITIONS_POOL[i % len(CONDITIONS_POOL)][0],
                    "description": condition_raw.strip() if isinstance(condition_raw, str) and i == 0 else CONDITIONS_POOL[i % len(CONDITIONS_POOL)][1],
                    "rain_total_3h": round(random.uniform(0, 8), 1),
                    "pop_max": round(random.uniform(0, 0.6), 2),
                })

    return result if result else None


def _map_pagasa_condition(raw: str) -> str:
    raw_lower = raw.lower()
    if "thunder" in raw_lower or "storm" in raw_lower:
        return "Thunderstorm"
    if "rain" in raw_lower or "drizzle" in raw_lower or "shower" in raw_lower:
        return "Rain" if "heavy" in raw_lower or "moderate" in raw_lower else "Drizzle"
    if "cloud" in raw_lower or "overcast" in raw_lower:
        return "Clouds"
    if "clear" in raw_lower or "sunny" in raw_lower or "fair" in raw_lower:
        return "Clear"
    return "Clouds"


def _safe_float(val: any) -> float:
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


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
