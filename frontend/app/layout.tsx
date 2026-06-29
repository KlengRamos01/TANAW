import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "TANAW — Weather-Aware Destination Planner",
  description: "Find Philippine destinations with the best weather for your next trip.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#F5F0E8] text-gray-900 min-h-screen`}>{children}</body>
    </html>
  )
}
