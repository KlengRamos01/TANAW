const styles: Record<string, string> = {
  green: "bg-green-100 text-green-800 border-green-300",
  yellow: "bg-yellow-100 text-yellow-800 border-yellow-300",
  red: "bg-red-100 text-red-800 border-red-300",
}

const labels: Record<string, string> = {
  green: "Safe",
  yellow: "Caution",
  red: "Avoid",
}

export default function RiskBadge({ level }: { level: string }) {
  const normalized = level.toLowerCase() === "green" ? "green" : level.toLowerCase() === "red" ? "red" : "yellow"
  return (
    <span
      className={`inline-block px-3 py-1 rounded-full text-xs font-semibold border ${styles[normalized]}`}
    >
      {labels[normalized]}
    </span>
  )
}
