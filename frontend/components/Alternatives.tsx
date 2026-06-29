import RiskBadge from "./RiskBadge"

interface AlternativeDest {
  id: number
  name: string
  municipality: string
  province: string
  region: string
  latitude: number
  longitude: number
  category: string
}

interface Alternative {
  destination: AlternativeDest
  distance_km: number
  travel_time_estimate: string
}

interface AlternativesData {
  origin_id: number
  origin_name: string
  island_group: string
  alternatives: Alternative[]
  total_found: number
  requested: number
  note: string | null
}

export default function Alternatives({ data }: { data: AlternativesData }) {
  return (
    <div className="mt-10 w-full max-w-4xl">
      <div className="border-t border-gray-200 pt-8">
        <h3 className="text-lg font-bold text-gray-900 mb-1">
          {data.alternatives.length > 0
            ? `Green-rated alternatives in ${data.island_group}`
            : data.note || "No alternatives found"}
        </h3>
        {data.note && data.alternatives.length > 0 && (
          <p className="text-sm text-gray-500 mb-4">{data.note}</p>
        )}
        {data.note && data.alternatives.length === 0 && (
          <p className="text-sm text-gray-500">{data.note}</p>
        )}

        {data.alternatives.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.alternatives.map((alt) => (
              <div
                key={alt.destination.id}
                className="bg-green-50 border border-green-200 rounded-xl p-5 flex flex-col gap-2"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{alt.destination.name}</p>
                    <p className="text-sm text-gray-500">
                      {alt.destination.municipality && `${alt.destination.municipality}, `}
                      {alt.destination.province}
                    </p>
                  </div>
                  <RiskBadge level="green" />
                </div>
                <div className="flex gap-3 text-xs text-gray-500">
                  <span>{alt.distance_km} km</span>
                  <span>&middot;</span>
                  <span>~{alt.travel_time_estimate} drive</span>
                </div>
                <p className="text-xs text-gray-400 capitalize">{alt.destination.category}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
