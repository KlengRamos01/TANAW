# TANAW — Weather-Aware Destination Planner

## Overview
TANAW ("tan-awa" — to look/see in Cebuano) is a web and mobile app that gives Filipinos clear, location-specific weather forecasts for the days ahead. It tells them which destinations to avoid due to storms or unsafe conditions and recommends nearby places with better weather instead.

## Core Features
1. **Destination Search with Plain-Language Daily Breakdown** — Search any PH destination and get a forecast in conversational Filipino/English. ✅
2. **Three-Tier Destination Risk Badge (Red / Yellow / Green)** — At-a-glance safety rating per destination per day. ✅
3. **Alternative Destination Suggestions (Same Island Group, Better Forecast)** — Up to 3 nearby Green or Yellow-rated alternatives when a destination has Red/Yellow overall risk. Each alternative shows its true risk color badge (green or yellow). ✅
4. **Saved Trip Alerts with Risk-Change Notifications** — ❌ NOT INCLUDED IN V1
5. **Data Source and Timestamp Disclosure on Every Forecast** — Transparent data provenance on all weather data shown. ✅

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 + Tailwind CSS |
| AI / LLM | Google Gemini API (via google-generativeai) |
| Backend | Python 3.12+ (FastAPI, Uvicorn) |
| Testing | pytest |
| Data Sources | OpenWeatherMap API (primary), PAGASA website scrape (secondary) — no mock data |
| Deploy | Vercel (frontend) + GitHub Actions (backend CI/CD) |

## Architecture
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Next.js 14  │────▶│  FastAPI      │────▶│  Supabase    │
│  (Vercel)    │     │  (Python)     │     │  (DB + Auth) │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌─────────────┐     ┌──────────────────┐
│ Tailwind CSS │     │ Google Gemini API│
│ (UI)         │     │ + OpenWeather    │
└─────────────┘     └──────────────────┘
```

## Directory Structure
```
TANAW/
├── AGENTS.md              # This file
├── .env                   # Local environment variables (git-ignored)
├── .env.example           # Environment variable template
├── .gitignore
├── backend/               # Python FastAPI backend
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── models.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── data/
│       │   ├── __init__.py
│       │   └── destinations.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── alternatives.py
│       │   ├── gemini.py
│       │   ├── risk.py
│       │   └── weather.py
│       └── tests/
│           ├── __init__.py
│           └── test_risk.py
├── frontend/              # Next.js 14 application
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── components/
│       ├── Alternatives.tsx
│       ├── DestinationSearch.tsx
│       ├── ForecastCard.tsx
│       └── RiskBadge.tsx
└── .github/workflows/     # CI/CD pipelines
    └── deploy.yml
```

## Setup (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment
Copy `.env.example` to `.env` and fill in the required API keys.

**Note:** The app requires at least one data source to work. To use real data:
- `GEMINI_API_KEY` — Google Gemini API key for plain-language summaries
- `WEATHER_API_KEY` — OpenWeatherMap API key (primary weather source via RapidAPI `/fivedaysforcast`)
- `PAGASA_API_KEY` — not required; PAGASA data is scraped from `bagong.pagasa.dost.gov.ph`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/destinations/search?query=` | Search destinations (top 50) |
| GET | `/api/forecast?destination_id=&destination_name=&start_date=&end_date=` | Get 7-day forecast |
| GET | `/api/alternatives?destination_id=&start_date=&end_date=` | Get 3 closest Green/Yellow alternatives |

## Feature 1 — 7-Day Destination Search

- Search any of 50 pre-loaded Philippine tourist destinations
- Returns 7-day forecast cards with plain-language summaries (via Gemini)
- Three-tier risk badges: green (safe), yellow (caution), red (avoid)
- Data source + timestamp disclosed on every forecast

## Feature 2 — Travel-safe Destinations

- When the origin destination shows Red or Yellow overall risk, up to 3 alternatives from the same island group are suggested
- Each alternative shows its **true risk badge** (green or yellow) — not forced to green
- Ranked by proximity — includes distance (km) and estimated travel time
- Section titled "Travel-safe Destinations in {island group}"

## Commit Conventions
- `feat:` — new feature
- `fix:` — bug fix
- `chore:` — maintenance / tooling
- `docs:` — documentation
- `refactor:` — code restructuring
