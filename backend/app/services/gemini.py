import re
from datetime import datetime

from app.config import settings

MOCK_SUMMARIES = [
    ("Clear", "green", "Sunny skies and calm winds — perfect for outdoor adventures!"),
    ("Clouds", "yellow", "Cloudy with occasional showers, better bring an umbrella when going out."),
    ("Rain", "red", "Moderate to heavy rain expected, roads may become slippery so drive carefully."),
    ("Clouds", "yellow", "Overcast skies with intermittent rain, outdoor plans might need a backup."),
    ("Rain", "red", "Light to moderate rain throughout the day, beach trips are not advisable."),
    ("Clear", "green", "Fair weather with mild winds, ideal for island hopping and tours."),
    ("Thunderstorm", "red", "Thunderstorms likely in the afternoon, postpone outdoor excursions."),
]


async def generate_forecast_summaries(daily_data: list[dict], destination_name: str) -> list[dict[str, str]]:
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if not settings.gemini_api_key:
        return _fallback_summaries(daily_data, day_names)

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = _build_prompt(daily_data, destination_name)
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 1024, "temperature": 0.3})
        return _parse_response(response.text, daily_data, day_names)
    except Exception:
        return _fallback_summaries(daily_data, day_names)


def _build_prompt(daily_data: list[dict], destination_name: str) -> str:
    lines = []
    for d in daily_data:
        lines.append(
            f"- {d['date']}: {d['condition']} ({d['description']}), "
            f"temp {d['temp_min']}-{d['temp_max']}°C, "
            f"humidity {d['humidity_avg']}%, "
            f"wind up to {d['wind_speed_max']} m/s, "
            f"rain {d['rain_total_3h']}mm, "
            f"precip chance {d['pop_max'] * 100:.0f}%"
        )

    return f"""You are a weather analyst for the Philippines. Given raw weather data for {destination_name}, generate a 7-day forecast.

For each day, output EXACTLY one line:
DayName | RiskLevel | One plain-language sentence about weather and travel impact.

RiskLevel must be one of: green (safe), yellow (caution), red (dangerous/avoid).

Example:
Monday | green | Sunny with light breezes, great for beach trips and island tours.

CRITICAL: One line per day. No extra text before or after. No markdown.

Data:
{chr(10).join(lines)}"""


def _parse_response(text: str, daily_data: list[dict], day_names: list[str]) -> list[dict[str, str]]:
    results = []
    lines = text.strip().split("\n")

    for i, line in enumerate(lines):
        line = line.strip()
        if not line or "|" not in line:
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue

        risk = parts[1].strip().lower()
        if risk not in ("green", "yellow", "red"):
            risk = "yellow"

        summary = parts[2].strip()

        day_idx = i if i < len(daily_data) else len(daily_data) - 1
        date = daily_data[day_idx]["date"] if day_idx < len(daily_data) else ""
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            day_name = dt.strftime("%A")
        except (ValueError, IndexError):
            day_name = day_names[day_idx % 7] if day_idx < 7 else ""

        results.append({
            "date": date,
            "day_name": day_name,
            "risk_level": risk,
            "summary": summary,
        })

    return results


def _fallback_summaries(daily_data: list[dict], day_names: list[str]) -> list[dict[str, str]]:
    results = []
    for i, day in enumerate(daily_data):
        try:
            dt = datetime.strptime(day["date"], "%Y-%m-%d")
            day_name = dt.strftime("%A")
        except ValueError:
            day_name = day_names[i % 7]

        fallback = _generate_fallback(day["condition"])
        results.append({
            "date": day["date"],
            "day_name": day_name,
            "risk_level": fallback[1],
            "summary": fallback[2],
        })
    return results


def _generate_fallback(condition: str) -> tuple:
    for key, risk, summary in MOCK_SUMMARIES:
        if key == condition:
            return (key, risk, summary)
    return ("Clouds", "yellow", "Cloudy skies with a chance of rain, plan accordingly.")
