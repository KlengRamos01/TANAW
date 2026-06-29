const colorStyles: Record<string, string> = {
  green: "bg-green-100 text-green-800 border-green-300",
  yellow: "bg-yellow-100 text-yellow-800 border-yellow-300",
  red: "bg-red-100 text-red-800 border-red-300",
}

const labels: Record<string, string> = {
  green: "Safe",
  yellow: "Caution",
  red: "Avoid",
}

const sizeStyles: Record<string, string> = {
  sm: "px-3 py-1 text-xs",
  md: "px-4 py-1.5 text-sm",
  lg: "px-6 py-2.5 text-base font-bold",
}

export default function RiskBadge({ level, size = "sm" }: { level: string; size?: "sm" | "md" | "lg" }) {
  const normalized = level === "green" ? "green" : level === "red" ? "red" : "yellow"
  return (
    <span
      className={`inline-block rounded-full font-semibold border ${colorStyles[normalized]} ${sizeStyles[size]}`}
    >
      {labels[normalized]}
    </span>
  )
}
