'use client'

import { useState } from 'react'

interface SidebarProps {
  collection: string
  setCollection: (value: string) => void
  limit: number
  setLimit: (value: number) => void
  showSources: boolean
  setShowSources: (value: boolean) => void
  useHybrid: boolean
  setUseHybrid: (value: boolean) => void
  useReranking: boolean
  setUseReranking: (value: boolean) => void
  extractCitations: boolean
  setExtractCitations: (value: boolean) => void
  queryHistory: string[]
  onHistoryClick: (query: string) => void
  onQuickSearch: (query: string) => void
  onDeleteHistory: (index: number) => void
  onClearHistory: () => void
}

export default function Sidebar({
  collection,
  setCollection,
  limit,
  setLimit,
  showSources,
  setShowSources,
  useHybrid,
  setUseHybrid,
  useReranking,
  setUseReranking,
  extractCitations,
  setExtractCitations,
  queryHistory,
  onHistoryClick,
  onQuickSearch,
  onDeleteHistory,
  onClearHistory
}: SidebarProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    history: false,
    settings: true,
    filters: false
  })

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }))
  }

  const quickSearchButtons = [
    { label: "☠️ Termination", query: "What are termination clauses in software licenses?" },
    { label: "💰 Payment", query: "What are payment terms and conditions?" },
    { label: "📋 Warranties", query: "What are warranty provisions in commercial agreements?" },
    { label: "🧠 IP Rights", query: "How are intellectual property rights transferred?" },
    { label: "⚠️ Liability", query: "What are limitations of liability?" },
    { label: "🛡️ Indemnity", query: "What are indemnification provisions?" },
  ]

  return (
    <aside className="w-80 bg-harvey-dark border-r border-gray-800 flex-shrink-0 overflow-y-auto h-screen sticky top-0">
      <div className="p-6">
        {/* Query History */}
        {queryHistory.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <button
                onClick={() => toggleSection('history')}
                className="flex-1 text-left text-sm font-normal text-gray-400 py-2 flex justify-between items-center hover:text-white transition-colors"
              >
                Query History ({queryHistory.length})
                <span>{expandedSections.history ? '−' : '+'}</span>
              </button>
              {queryHistory.length > 5 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    if (confirm('Clear all query history?')) {
                      onClearHistory()
                    }
                  }}
                  className="ml-2 text-xs text-gray-600 hover:text-red-400 transition-colors px-2 py-1"
                  title="Clear all history"
                >
                  Clear
                </button>
              )}
            </div>
            {expandedSections.history && (
              <div className="mt-2 space-y-2">
                {queryHistory.slice().reverse().slice(0, 15).map((histQuery, idx) => {
                  const originalIndex = queryHistory.length - 1 - idx
                  return (
                    <div
                      key={idx}
                      className="group flex items-center gap-2 w-full text-xs text-gray-500 hover:text-white hover:bg-gray-900 px-3 py-2 rounded-md transition-colors border border-transparent hover:border-gray-800"
                    >
                      <button
                        onClick={() => onHistoryClick(histQuery)}
                        className="flex-1 text-left truncate"
                        title={histQuery}
                      >
                        {histQuery.length > 45 ? histQuery.substring(0, 45) + '...' : histQuery}
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onDeleteHistory(originalIndex)
                        }}
                        className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-red-400 transition-all px-1"
                        title="Delete this query"
                      >
                        ×
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {/* Quick Search Buttons */}
        <div className="mb-6">
          <h3 className="text-sm font-normal text-gray-400 mb-3">Quick Search</h3>
          <div className="grid grid-cols-2 gap-2">
            {quickSearchButtons.map((button, idx) => (
              <button
                key={idx}
                onClick={() => onQuickSearch(button.query)}
                className="px-3 py-2 text-xs text-gray-500 hover:text-white hover:bg-gray-900 rounded-md transition-colors border border-gray-800 hover:border-gray-700"
              >
                {button.label}
              </button>
            ))}
          </div>
        </div>

        {/* Settings */}
        <div className="mb-6">
          <button
            onClick={() => toggleSection('settings')}
            className="w-full text-left text-sm font-normal text-gray-400 py-2 flex justify-between items-center hover:text-white transition-colors"
          >
            Settings
            <span>{expandedSections.settings ? '−' : '+'}</span>
          </button>
          {expandedSections.settings && (
            <div className="mt-3 space-y-4">
              <div>
                <label className="block text-xs font-normal text-gray-500 mb-2">
                  Search in:
                </label>
                <select
                  value={collection}
                  onChange={(e) => setCollection(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-800 rounded-md bg-harvey-dark text-white text-xs focus:border-white focus:outline-none transition-colors"
                >
                  <option value="both">Contracts & Cases</option>
                  <option value="contracts">Contracts Only</option>
                  <option value="cases">Cases Only</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-normal text-gray-500 mb-2">
                  Number of Results: {limit}
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={limit}
                  onChange={(e) => setLimit(parseInt(e.target.value))}
                  className="w-full accent-white"
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={showSources}
                  onChange={(e) => setShowSources(e.target.checked)}
                  className="mr-2 w-4 h-4 accent-white"
                />
                <label className="text-xs text-gray-500">Show Source Documents</label>
              </div>
            </div>
          )}
        </div>

        {/* Advanced Filters */}
        <div className="mb-6">
          <button
            onClick={() => toggleSection('filters')}
            className="w-full text-left text-sm font-normal text-gray-400 py-2 flex justify-between items-center hover:text-white transition-colors"
          >
            Advanced Filters
            <span>{expandedSections.filters ? '−' : '+'}</span>
          </button>
          {expandedSections.filters && (
            <div className="mt-3 space-y-3">
              <p className="text-xs text-gray-600 mb-2 font-light">Search Methods:</p>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={useHybrid}
                    onChange={(e) => setUseHybrid(e.target.checked)}
                    className="mr-2 w-4 h-4 accent-white"
                  />
                  <span className="text-xs text-gray-500">Hybrid Search (Semantic + Keyword)</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={useReranking}
                    onChange={(e) => setUseReranking(e.target.checked)}
                    className="mr-2 w-4 h-4 accent-white"
                  />
                  <span className="text-xs text-gray-500">Cross-Encoder Reranking</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={extractCitations}
                    onChange={(e) => setExtractCitations(e.target.checked)}
                    className="mr-2 w-4 h-4 accent-white"
                  />
                  <span className="text-xs text-gray-500">Extract Citations</span>
                </label>
              </div>
              <div className="pt-3 border-t border-gray-800">
                <p className="text-xs text-gray-600 italic font-light">
                  ℹ️ Date, Jurisdiction, and Court filters are currently disabled as they require indexed metadata.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* System Status */}
        <div className="mt-8 pt-6 border-t border-gray-800">
          <h3 className="text-sm font-normal text-gray-400 mb-4">System Status</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-gray-600 mb-1 font-light">Documents</p>
              <p className="text-lg font-serif-heading text-white">5,511</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1 font-light">Chunks</p>
              <p className="text-lg font-serif-heading text-white">276,970</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1 font-light">Courts</p>
              <p className="text-lg font-serif-heading text-white">6</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1 font-light">Vectors</p>
              <p className="text-lg font-serif-heading text-white">384-dim</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}

