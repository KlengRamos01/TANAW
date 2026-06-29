"use client"

import { useState } from "react"
import DestinationSearch from "../components/DestinationSearch"
import ForecastCard from "../components/ForecastCard"

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
  summary: string
}

interface ForecastResponse {
  destination: Destination
  forecasts: Forecast[]
  data_source: string
  generated_at: string
}

export default function Home() {
  const [forecast, setForecast] = useState<ForecastResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function handleSelect(dest: Destination) {
    setLoading(true)
    setError("")
    setForecast(null)

    try {
      const res = await fetch(`http://localhost:8000/api/forecast/${dest.id}`)
      if (!res.ok) throw new Error("Failed to load forecast")
      const data: ForecastResponse = await res.json()
      setForecast(data)
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
        Try: El Nido, Boracay, Siargao, Baguio, or any of 50 PH destinations
      </div>

      {loading && (
        <div className="mt-12 flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-500 text-sm">Fetching 7-day forecast...</p>
        </div>
      )}

      {error && (
        <div className="mt-12 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm max-w-md">
          {error}
        </div>
      )}

      {forecast && (
        <div className="mt-12 w-full max-w-4xl">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              {forecast.destination.name}
            </h2>
            <p className="text-gray-500">
              {forecast.destination.municipality}, {forecast.destination.province} &middot;{" "}
              <span className="capitalize">{forecast.destination.category}</span>
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {forecast.forecasts.map((day) => (
              <ForecastCard
                key={day.date}
                dayName={day.day_name}
                date={day.date}
                riskLevel={day.risk_level}
                summary={day.summary}
              />
            ))}
          </div>

          <div className="mt-8 text-center text-xs text-gray-400">
            Data source: {forecast.data_source} &middot; Generated at{" "}
            {new Date(forecast.generated_at).toLocaleString("en-PH")}
          </div>
        </div>
      )}
    </main>
  )
}
