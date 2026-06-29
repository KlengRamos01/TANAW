"use client"

import { useState, useRef, useEffect } from "react"

interface Destination {
  id: number
  name: string
  municipality: string
  province: string
  region: string
  category: string
}

export default function DestinationSearch({
  onSelect,
}: {
  onSelect: (dest: Destination) => void
}) {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<Destination[]>([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [])

  async function handleInput(value: string) {
    setQuery(value)
    if (value.trim().length < 1) {
      setResults([])
      setOpen(false)
      return
    }

    setLoading(true)
    try {
      const res = await fetch(`http://localhost:8000/api/destinations/search?query=${encodeURIComponent(value)}`)
      if (!res.ok) {
        setResults([])
        setOpen(true)
        return
      }
      const data = await res.json()
      setResults(data.destinations)
      setOpen(true)
    } catch {
      setResults([])
      setOpen(true)
    } finally {
      setLoading(false)
    }
  }

  function select(dest: Destination) {
    setQuery(`${dest.name}, ${dest.province}`)
    setOpen(false)
    onSelect(dest)
  }

  return (
    <div ref={ref} className="relative w-full max-w-xl">
      <input
        type="text"
        value={query}
        onChange={(e) => handleInput(e.target.value)}
        placeholder="Search a destination... (e.g. El Nido, Boracay)"
        className="w-full px-5 py-4 rounded-xl border border-gray-300 bg-white shadow-sm text-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      {loading && (
        <div className="absolute right-4 top-1/2 -translate-y-1/2">
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {open && results.length > 0 && (
        <ul className="absolute z-10 mt-2 w-full bg-white rounded-xl shadow-lg border border-gray-200 max-h-72 overflow-y-auto">
          {results.map((dest) => (
            <li
              key={dest.id}
              onClick={() => select(dest)}
              className="px-5 py-3 cursor-pointer hover:bg-blue-50 transition-colors border-b border-gray-100 last:border-0"
            >
              <span className="font-medium">{dest.name}</span>
              <span className="text-gray-500 text-sm ml-2">
                {dest.municipality}, {dest.province}
              </span>
              <span className="text-gray-400 text-xs ml-2 capitalize">({dest.category})</span>
            </li>
          ))}
        </ul>
      )}

      {open && query.trim().length >= 1 && !loading && results.length === 0 && (
        <div className="absolute z-10 mt-2 w-full bg-white rounded-xl shadow-lg border border-gray-200 p-5 text-center text-gray-500">
          No destinations found. Try a different search term.
        </div>
      )}
    </div>
  )
}
