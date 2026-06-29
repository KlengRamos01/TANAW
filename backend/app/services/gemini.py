from datetime import datetime

from app.config import settings

MOCK_SUMMARIES_BY_RISK = {
    "green": "Sunny skies and calm winds — perfect for outdoor adventures!",
    "yellow": "Cloudy with occasional showers, better bring an umbrella when going out.",
    "red": "Moderate to heavy rain expected, roads may become slippery so drive carefully.",
}

MOCK_SUMMARIES_BY_CONDITION = {
    "Clear": "Sunny skies and calm winds — perfect for outdoor adventures!",
    "Clouds": "Cloudy with occasional showers, better bring an umbrella when going out.",
    "Rain": "Moderate to heavy rain expected, roads may become slippery so drive carefully.",
    "Thunderstorm": "Thunderstorms likely in the afternoon, postpone outdoor excursions.",
    "Drizzle": "Light drizzle expected, pack a light raincoat just in case.",
}


async def generate_summaries(daily_forecasts: list[dict], destination_name: str) -> list[str]:
    if not settings.gemini_api_key:
        return _fallback_summaries(daily_forecasts)

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = _build_prompt(daily_forecasts, destination_name)
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 1024, "temperature": 0.3})

        parsed = _parse_response(response.text, len(daily_forecasts))
        if len(parsed) == len(daily_forecasts):
            return parsed
    except Exception:
        pass

    return _fallback_summaries(daily_forecasts)


def _build_prompt(forecasts: list[dict], destination_name: str) -> str:
    lines = []
    for f in forecasts:
        risk_badge = f["risk_level"].upper()
        lines.append(
            f"- {f['day_name']} ({f['date']}): risk={risk_badge}, "
            f"wind {f.get('wind_speed_max', 0)} m/s, "
            f"rain {f.get('rain_total_3h', 0)}mm, "
            f"{f.get('condition', '')} ({f.get('description', '')})"
        )

    return f"""You are a weather analyst for the Philippines. Given the risk-assessed forecast for {destination_name}, write one plain-language sentence per day explaining the weather impact.

Risk levels are already calculated. Your job is ONLY to write the sentence.

For each day, output EXACTLY one line with just the sentence, no prefix or labels.

Example outputs:
Sunny with light breezes, great for beach trips and island tours.
Heavy rain and strong winds expected, ferry crossings may be disrupted.

Data:
{chr(10).join(lines)}"""


def _parse_response(text: str, expected_count: int) -> list[str]:
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    out = []
    for line in lines:
        if "|" in line:
            parts = line.split("|")
            if len(parts) >= 3:
                line = parts[-1].strip()
        if len(line) > 10:
            out.append(line)
    return out[:expected_count]


def _fallback_summaries(forecasts: list[dict]) -> list[str]:
    summaries = []
    for f in forecasts:
        condition = f.get("condition", "")
        risk = f.get("risk_level", "yellow")

        if risk == "red":
            base = MOCK_SUMMARIES_BY_CONDITION.get(condition) or MOCK_SUMMARIES_BY_RISK["red"]
        elif risk == "yellow":
            base = MOCK_SUMMARIES_BY_CONDITION.get(condition) or MOCK_SUMMARIES_BY_RISK["yellow"]
        else:
            base = MOCK_SUMMARIES_BY_CONDITION.get(condition) or MOCK_SUMMARIES_BY_RISK["green"]

        summaries.append(base)

    return summaries
