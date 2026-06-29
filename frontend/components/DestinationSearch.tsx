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
  const inputRef = useRef<HTMLInputElement>(null)
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
      const data = await res.json()
      setResults(data.destinations || [])
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
    setOpen(true)
  }

  function select(dest: Destination) {
    setQuery(`${dest.name}, ${dest.province || "Philippines"}`)
    setOpen(false)
    onSelect(dest)
  }

  function clearQuery() {
    setQuery("")
    setResults([])
    setOpen(false)
    inputRef.current?.focus()
  }

  function searchDynamic() {
    const trimmed = query.trim()
    if (!trimmed) return
    select({ id: 0, name: trimmed, municipality: "", province: "", region: "", category: "" })
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") {
      searchDynamic()
    }
  }

  return (
    <div ref={ref} className="relative w-full max-w-xl">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => handleInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search a Philippine destination..."
          className="w-full px-5 py-4 pr-20 rounded-xl border border-gray-300 bg-white shadow-sm text-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {query && (
          <button
            onClick={clearQuery}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700 transition-colors"
            aria-label="Clear search"
          >
            <svg viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16ZM8.28 7.22a.75.75 0 0 0-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 1 0 1.06 1.06L10 11.06l1.72 1.72a.75.75 0 1 0 1.06-1.06L11.06 10l1.72-1.72a.75.75 0 0 0-1.06-1.06L10 8.94 8.28 7.22Z" clipRule="evenodd" />
            </svg>
          </button>
        )}
        {loading && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}
      </div>

      <p className="text-xs text-gray-400 mt-2 text-center">Press enter to submit</p>

      {open && query.trim().length >= 1 && (
        <ul className="absolute z-10 mt-2 w-full bg-white rounded-xl shadow-lg border border-gray-200 max-h-72 overflow-y-auto">
          {results.length > 0 && results.map((dest) => (
            <li
              key={dest.id}
              onMouseDown={(e) => { e.preventDefault(); select(dest) }}
              className="px-5 py-3 cursor-pointer hover:bg-blue-50 transition-colors border-b border-gray-100"
            >
              <span className="font-medium">{dest.name}</span>
              <span className="text-gray-500 text-sm ml-2">
                {dest.municipality && `${dest.municipality}, `}{dest.province}
              </span>
              <span className="text-gray-400 text-xs ml-2 capitalize">({dest.category})</span>
            </li>
          ))}
          <li
            onMouseDown={(e) => { e.preventDefault(); searchDynamic() }}
            className="px-5 py-3 cursor-pointer hover:bg-blue-50 transition-colors text-blue-600 font-medium"
          >
            {results.length > 0 ? `Also search "${query.trim()}" as a Philippine destination →` : `Search "${query.trim()}" as a Philippine destination →`}
          </li>
        </ul>
      )}
    </div>
  )
}
