import RiskBadge from "./RiskBadge"

interface ForecastProps {
  dayName: string
  date: string
  riskLevel: string
  riskReason: string
  summary: string
}

export default function ForecastCard({ dayName, date, riskLevel, riskReason, summary }: ForecastProps) {
  const formattedDate = new Date(date + "T12:00:00").toLocaleDateString("en-PH", {
    month: "short",
    day: "numeric",
  })

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col gap-2 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-semibold text-gray-900">{dayName}</p>
          <p className="text-sm text-gray-500">{formattedDate}</p>
        </div>
        <RiskBadge level={riskLevel} />
      </div>
      <p className="text-xs text-gray-400 italic">{riskReason}</p>
      <p className="text-gray-700 text-sm leading-relaxed">{summary}</p>
    </div>
  )
}
