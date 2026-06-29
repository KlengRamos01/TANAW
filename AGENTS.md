# TANAW — Weather-Aware Destination Planner

## Overview
TANAW ("tan-awa" — to look/see in Cebuano) is a web and mobile app that gives Filipinos clear, location-specific weather forecasts for the days ahead. It tells them which destinations to avoid due to storms or unsafe conditions and recommends nearby places with better weather instead.

## Core Features
1. ** Destination Search with Plain-Language Daily Breakdown** — Search any PH destination and get a forecast in conversational Filipino/English.
2. **Three-Tier Destination Risk Badge (Red / Yellow / Green)** — At-a-glance safety rating per destination per day.
3. **Alternative Destination Suggestions (Same Region, Better Forecast)** — AI-recommended nearby alternatives when a destination has poor weather.
4. **NOT INCLUDED IN V1-Saved Trip Alerts with Risk-Change Notifications** — Monitor saved trips and get notified when the risk level changes.
5. **Data Source and Timestamp Disclosure on Every Forecast** — Transparent data provenance on all weather data shown.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 + Tailwind CSS |
| AI / LLM | Google Gemini API (via google-generativeai) |
| Backend | Python (FastAPI) |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth |
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
│       └── services/
│           ├── __init__.py
│           ├── weather.py
│           └── gemini.py
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

**Note:** The app works without API keys using mock/fallback data. To use real data:
- `GEMINI_API_KEY` — Google Gemini API key for plain-language summaries
- `WEATHER_API_KEY` — OpenWeatherMap API key for weather data

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/destinations/search?query=` | Search destinations (top 50) |
| GET | `/api/forecast/{destination_id}` | Get 7-day forecast |

## Feature 1 — 7-Day Destination Search

- Search any of 50 pre-loaded Philippine tourist destinations
- Returns 7-day forecast cards with plain-language summaries (via Gemini or fallback)
- Three-tier risk badges: green (safe), yellow (caution), red (avoid)
- Data source + timestamp disclosed on every forecast

## Commit Conventions
- `feat:` — new feature
- `fix:` — bug fix
- `chore:` — maintenance / tooling
- `docs:` — documentation
- `refactor:` — code restructuring
