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
        <h1 className="text-5xl font-bold tracking-tight text-gray-900">TANAW</h1>
        <p className="text-lg text-gray-500 mt-2">Weather-Aware Destination Planner</p>
        <p className="text-sm text-gray-400 mt-1">Know before you go.</p>
      </div>

      <DestinationSearch onSelect={handleSelect} />

      <div className="mt-4 text-xs text-gray-400">
        Search a Philippine destination
      </div>

      {showDatePicker && selectedDest && !forecast && !loading && (
        <div className="mt-8 w-full max-w-xl bg-white rounded-xl shadow-sm border border-gray-200 p-6">
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
          <div className="mb-6 flex items-start justify-between flex-wrap gap-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {forecast.destination.name}
              </h2>
              <p className="text-gray-500">
                {forecast.destination.municipality}
                {forecast.destination.province ? `, ${forecast.destination.province}` : ""}
                {forecast.destination.region ? ` · ${forecast.destination.region}` : ""}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {startDate} to {endDate} · {forecast.forecasts.length} days
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500 mb-1">Trip Risk</p>
              <RiskBadge level={forecast.overall_trip_risk.level} size="lg" />
              <p className="text-xs text-gray-500 mt-2 max-w-xs">
                {forecast.overall_trip_risk.reason}
              </p>
            </div>
          </div>

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

          <div className="mt-8 text-center text-xs text-gray-400">
            Risk ruleset: PAGASA storm signal thresholds + rainfall + wind speed + sea conditions &middot;{" "}
            Data source: {forecast.data_source} &middot; Generated at{" "}
            {new Date(forecast.generated_at).toLocaleString("en-PH")}
          </div>

          {alternatives && <Alternatives data={alternatives} />}
        </div>
      )}
    </main>
  )
}
