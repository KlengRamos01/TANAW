import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "TANAW — Weather-Aware Destination Planner",
  description: "Find Philippine destinations with the best weather for your next trip.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen">{children}</body>
    </html>
  )
}
