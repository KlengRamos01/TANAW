import RiskBadge from "./RiskBadge"

interface ForecastProps {
  dayName: string
  date: string
  riskLevel: string
  riskReason: string
  summary: string
}

function getWeatherType(riskLevel: string, riskReason: string, summary: string): "sunny" | "cloudy" | "rainy" | "stormy" {
  const text = (riskReason + " " + summary).toLowerCase()
  if (riskLevel === "green") return "sunny"
  if (text.includes("storm signal")) return "stormy"
  if (text.includes("thunderstorm")) return "stormy"
  if (text.includes("heavy rain") || text.includes("moderate to heavy rain")) return "rainy"
  if (text.includes("rain") || text.includes("drizzle") || text.includes("shower")) return "rainy"
  if (text.includes("cloud") || text.includes("overcast")) return "cloudy"
  if (text.includes("scattered") || text.includes("occasional")) return "cloudy"
  if (riskLevel === "red") return "rainy"
  if (riskLevel === "yellow") return "cloudy"
  return "sunny"
}

const weatherStyles: Record<string, { bg: string; text: string; icon: JSX.Element }> = {
  sunny: {
    bg: "bg-amber-50 border-amber-200",
    text: "text-amber-900",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-8 h-8 text-amber-500" stroke="currentColor" strokeWidth="1.5">
        <circle cx="12" cy="12" r="5" />
        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" strokeLinecap="round" />
      </svg>
    ),
  },
  cloudy: {
    bg: "bg-gray-200 border-gray-300",
    text: "text-gray-800",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-8 h-8 text-gray-500" stroke="currentColor" strokeWidth="1.5">
        <path d="M6.5 14A4.5 4.5 0 1 0 6.5 5a5.5 5.5 0 0 0-.5 9M4 14a4 4 0 0 0 4 4h8.5a3.5 3.5 0 1 0-.5-6.97" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  rainy: {
    bg: "bg-blue-900 border-blue-800",
    text: "text-blue-50",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-8 h-8 text-blue-300" stroke="currentColor" strokeWidth="1.5">
        <path d="M6.5 12A4.5 4.5 0 1 0 6.5 3a5.5 5.5 0 0 0-.5 9M4 12a4 4 0 0 0 4 4h8.5a3.5 3.5 0 1 0-.5-6.97" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M10 17l-1 3M14 17l-1 3M8 19l-1 2M16 19l-1 2" strokeLinecap="round" />
      </svg>
    ),
  },
  stormy: {
    bg: "bg-gray-900 border-gray-700",
    text: "text-gray-100",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-8 h-8 text-yellow-400" stroke="currentColor" strokeWidth="1.5">
        <path d="M6.5 12A4.5 4.5 0 1 0 6.5 3a5.5 5.5 0 0 0-.5 9M4 12a4 4 0 0 0 4 4h8.5a3.5 3.5 0 1 0-.5-6.97" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M12 15l-2 4h3l-1.5 4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
}

export default function ForecastCard({ dayName, date, riskLevel, riskReason, summary }: ForecastProps) {
  const formattedDate = new Date(date + "T12:00:00").toLocaleDateString("en-PH", {
    month: "short",
    day: "numeric",
  })

  const weather = getWeatherType(riskLevel, riskReason, summary)
  const style = weatherStyles[weather]

  return (
    <div className={`rounded-xl border p-5 flex flex-col gap-3 shadow-sm hover:shadow-md transition-shadow ${style.bg}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className={`font-semibold ${style.text}`}>{dayName}</p>
          <p className={`text-sm opacity-70 ${style.text}`}>{formattedDate}</p>
        </div>
        <RiskBadge level={riskLevel} />
      </div>
      <div className="flex items-center gap-2">
        {style.icon}
        <span className={`text-xs font-medium uppercase tracking-wider opacity-80 ${style.text}`}>
          {weather === "sunny" ? "Sunny" : weather === "cloudy" ? "Cloudy" : weather === "rainy" ? "Rain" : "Storm"}
        </span>
      </div>
      <p className={`text-xs italic opacity-60 ${style.text}`}>{riskReason}</p>
      <p className={`text-sm leading-relaxed ${style.text}`}>{summary}</p>
    </div>
  )
}
