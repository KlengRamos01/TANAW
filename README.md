# TANAW

A web and mobile app that gives Filipinos clear, location-specific weather forecasts for the days ahead, telling them which destinations to avoid due to storms or unsafe conditions, and recommending nearby places with better weather instead.

Travelers and residents across the Philippines lack a single tool that turns multi-day weather forecasts into clear, location-specific guidance and flagging which destinations to avoid due to storms or unsafe conditions and which nearby places have better weather instead, a gap felt daily by tourists, commuters, and event planners, especially during typhoon season. Today, they cobble together answers from scattered sources like PAGASA bulletins, generic weather apps, and social media storm updates, a slow and fragmented process that often delivers warnings too late and offers no actionable alternatives.

## Core Features

1. **Destination Search with Plain-Language Daily Breakdown** — Search any PH destination and get a day-by-day forecast in conversational Filipino/English, generated from PAGASA data and OpenWeatherMap via Gemini API.

2. **Three-Tier Destination Risk Badge (Red / Yellow / Green)** — Each destination gets a color-coded badge for the selected date range, calculated from a defined ruleset (PAGASA storm signal thresholds, rainfall, wind speed, sea conditions).

3. **Alternative Destination Suggestions (Same Island Group, Better Forecast)** — When a destination badge is Red or Yellow, the app shows up to 3 alternative destinations within the same island group (Luzon, Visayas, Mindanao) that have Green or Yellow badges for the same date range, ranked by proximity with distance and travel-time estimates.

4. **[NOT INCLUDED IN V1] Saved Trip Alerts with Risk-Change Notifications** — User saves a trip by entering a destination and date range. The app sends a push notification when the risk badge changes tier before the trip.

5. **Data Source and Timestamp Disclosure on Every Forecast** — Every forecast card displays the specific data source (OpenWeatherMap / PAGASA / Gemini) and a last-updated timestamp.

## Data Pipeline

| Priority | Source | Method |
|----------|--------|--------|
| Primary | OpenWeatherMap | RapidAPI (requires `WEATHER_API_KEY`) |
| Secondary | PAGASA | Website scrape of `bagong.pagasa.dost.gov.ph` tourist/city forecasts using BeautifulSoup |
| Fallback | Mock data | Deterministic random seed when no API keys or scrape available |
