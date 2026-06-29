"use client"

import { useState } from "react"
import Alternatives from "../components/Alternatives"
import DestinationSearch from "../components/DestinationSearch"
import ForecastCard from "../components/ForecastCard"
import RiskBadge from "../components/RiskBadge"

interface Destination {
  id: number
  name: string
  municipality: string
  province: string
  region: string
  category: string
}

interface Forecast {
  date: string
  day_name: string
  risk_level: string
  risk_reason: string
  summary: string
}

interface OverallTripRisk {
  level: string
  label: string
  color: string
  reason: string
}

interface ForecastResponse {
  destination: Destination
  forecasts: Forecast[]
  overall_trip_risk: OverallTripRisk
  data_source: string
  generated_at: string
}

function todayStr(): string {
  const d = new Date()
  return d.toISOString().slice(0, 10)
}

function weekFromNow(): string {
  const d = new Date()
  d.setDate(d.getDate() + 6)
  return d.toISOString().slice(0, 10)
}

export default function Home() {
  const [forecast, setForecast] = useState<ForecastResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [selectedDest, setSelectedDest] = useState<Destination | null>(null)
  const [startDate, setStartDate] = useState(todayStr())
  const [endDate, setEndDate] = useState(weekFromNow())
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [alternatives, setAlternatives] = useState<any>(null)

  async function handleSelect(dest: Destination) {
    setSelectedDest(dest)
    setShowDatePicker(true)
    setForecast(null)
    setError("")
  }

  async function loadForecast() {
    if (!selectedDest) return
    setLoading(true)
    setError("")
    setForecast(null)
    setAlternatives(null)

    try {
      const params = new URLSearchParams()
      params.set("start_date", startDate)
      params.set("end_date", endDate)

      if (selectedDest.id > 0) {
        params.set("destination_id", String(selectedDest.id))
      } else {
        params.set("destination_name", selectedDest.name)
      }

      const res = await fetch(`http://localhost:8000/api/forecast?${params}`)
      if (!res.ok) throw new Error("Failed to load forecast")
      const data: ForecastResponse = await res.json()
      setForecast(data)

      if (data.overall_trip_risk.level !== "green" && selectedDest.id > 0) {
        const altParams = new URLSearchParams()
        altParams.set("destination_id", String(selectedDest.id))
        altParams.set("start_date", startDate)
        altParams.set("end_date", endDate)
        altParams.set("region", selectedDest.region)
        const altRes = await fetch(`http://localhost:8000/api/alternatives?${altParams}`)
        if (altRes.ok) {
          setAlternatives(await altRes.json())
        }
      } else {
        setAlternatives(null)
      }
    } catch {
      setError("Could not load forecast. Make sure the backend is running.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-5xl font-bold tracking-tight text-gray-800">TANAW</h1>
        <p className="text-lg text-gray-600 mt-2">Weather-Aware Destination Planner</p>
        <p className="text-sm text-gray-500 mt-1">Know before you go.</p>
      </div>

      <DestinationSearch onSelect={handleSelect} />

      <div className="mt-4 text-xs text-gray-500">
        Search a Philippine destination
      </div>

      {showDatePicker && selectedDest && !forecast && !loading && (
        <div className="mt-8 w-full max-w-xl bg-white/90 backdrop-blur rounded-xl shadow-sm border border-gray-200 p-6">
          <p className="font-semibold text-gray-900 mb-3">
            When are you visiting {selectedDest.name}?
          </p>
          <div className="flex gap-4 items-end flex-wrap">
            <div>
              <label className="text-xs text-gray-500 block mb-1">Start date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">End date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={loadForecast}
              className="px-5 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors"
            >
              Check weather
            </button>
          </div>
        </div>
      )}

      {loading && (
        <div className="mt-12 flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-500 text-sm">Analyzing weather data and storm signals...</p>
        </div>
      )}

      {error && (
        <div className="mt-12 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm max-w-md">
          {error}
        </div>
      )}

      {forecast && (
        <div className="mt-12 w-full max-w-4xl">
          <OverallTripCard
            destinationName={forecast.destination.name}
            municipality={forecast.destination.municipality}
            province={forecast.destination.province}
            region={forecast.destination.region}
            startDate={startDate}
            endDate={endDate}
            daysCount={forecast.forecasts.length}
            overallLevel={forecast.overall_trip_risk.level}
            overallReason={forecast.overall_trip_risk.reason}
          />

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {forecast.forecasts.map((day) => (
              <ForecastCard
                key={day.date}
                dayName={day.day_name}
                date={day.date}
                riskLevel={day.risk_level}
                riskReason={day.risk_reason}
                summary={day.summary}
              />
            ))}
          </div>

          <div className="mt-8 text-center text-xs text-gray-500">
            Data source: {forecast.data_source} &middot;{" "}
            Generated at{" "}
            {new Date(forecast.generated_at).toLocaleString("en-PH")}
          </div>

          {alternatives && <Alternatives data={alternatives} />}
        </div>
      )}
    </main>
  )
}

function OverallTripCard({
  destinationName,
  municipality,
  province,
  region,
  startDate,
  endDate,
  daysCount,
  overallLevel,
  overallReason,
}: {
  destinationName: string
  municipality: string
  province: string
  region: string
  startDate: string
  endDate: string
  daysCount: number
  overallLevel: string
  overallReason: string
}) {
  function getOverallWeather(level: string, reason: string): "sunny" | "cloudy" | "rainy" | "stormy" {
    const text = reason.toLowerCase()
    if (level === "green") return "sunny"
    if (text.includes("storm signal")) return "stormy"
    if (text.includes("thunderstorm")) return "stormy"
    if (text.includes("heavy rain") || text.includes("heavy rainfall")) return "rainy"
    if (text.includes("rain") || text.includes("flood")) return "rainy"
    if (text.includes("cloud") || text.includes("scattered")) return "cloudy"
    if (level === "red") return "rainy"
    if (level === "yellow") return "cloudy"
    return "sunny"
  }

  const weather = getOverallWeather(overallLevel, overallReason)

  const styles: Record<string, { bg: string; text: string }> = {
    sunny: { bg: "bg-amber-50 border-amber-200", text: "text-amber-900" },
    cloudy: { bg: "bg-gray-200 border-gray-300", text: "text-gray-800" },
    rainy: { bg: "bg-blue-900 border-blue-800", text: "text-blue-50" },
    stormy: { bg: "bg-gray-900 border-gray-700", text: "text-gray-100" },
  }

  const s = styles[weather]

  const icons: Record<string, JSX.Element> = {
    sunny: (
      <svg viewBox="0 0 24 24" fill="none" className="w-10 h-10 text-amber-500" stroke="currentColor" strokeWidth="1.5">
        <circle cx="12" cy="12" r="5" />
        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" strokeLinecap="round" />
      </svg>
    ),
    cloudy: (
      <svg viewBox="0 0 24 24" fill="none" className="w-10 h-10 text-gray-500" stroke="currentColor" strokeWidth="1.5">
        <path d="M6.5 14A4.5 4.5 0 1 0 6.5 5a5.5 5.5 0 0 0-.5 9M4 14a4 4 0 0 0 4 4h8.5a3.5 3.5 0 1 0-.5-6.97" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    rainy: (
      <svg viewBox="0 0 24 24" fill="none" className="w-10 h-10 text-blue-300" stroke="currentColor" strokeWidth="1.5">
        <path d="M6.5 12A4.5 4.5 0 1 0 6.5 3a5.5 5.5 0 0 0-.5 9M4 12a4 4 0 0 0 4 4h8.5a3.5 3.5 0 1 0-.5-6.97" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M10 17l-1 3M14 17l-1 3M8 19l-1 2M16 19l-1 2" strokeLinecap="round" />
      </svg>
    ),
    stormy: (
      <svg viewBox="0 0 24 24" fill="none" className="w-10 h-10 text-yellow-400" stroke="currentColor" strokeWidth="1.5">
        <path d="M6.5 12A4.5 4.5 0 1 0 6.5 3a5.5 5.5 0 0 0-.5 9M4 12a4 4 0 0 0 4 4h8.5a3.5 3.5 0 1 0-.5-6.97" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M12 15l-2 4h3l-1.5 4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  }

  return (
    <div className={`rounded-xl border p-6 flex flex-col sm:flex-row items-start justify-between gap-4 shadow-sm hover:shadow-md transition-shadow mb-8 ${s.bg}`}>
      <div className="flex items-start gap-4">
        {icons[weather]}
        <div>
          <h2 className={`text-2xl font-bold ${s.text}`}>{destinationName}</h2>
          <p className={`text-sm opacity-70 ${s.text}`}>
            {municipality}{province ? `, ${province}` : ""}{region ? ` · ${region}` : ""}
          </p>
          <p className={`text-xs opacity-50 mt-1 ${s.text}`}>
            {startDate} to {endDate} · {daysCount} days
          </p>
        </div>
      </div>
      <div className="flex flex-col items-end gap-1 shrink-0">
        <span className={`text-xs font-medium uppercase tracking-wider opacity-60 ${s.text}`}>
          {weather === "sunny" ? "All Clear" : weather === "cloudy" ? "Caution" : weather === "rainy" ? "Heads Up" : "Avoid"}
        </span>
        <RiskBadge level={overallLevel} size="lg" />
        <p className={`text-xs mt-1 max-w-xs text-right opacity-70 ${s.text}`}>{overallReason}</p>
      </div>
    </div>
  )
}
