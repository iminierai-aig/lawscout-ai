'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import Sidebar from '@/components/Sidebar'

// Optimized axios instance with connection pooling and keep-alive
// This reduces connection overhead and improves performance
const apiClient = axios.create({
  timeout: 60000, // 60 second timeout for long queries
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    // Note: Accept-Encoding is a forbidden header - browsers handle compression automatically
  },
  // Enable HTTP keep-alive (reuse connections)
  httpAgent: typeof window === 'undefined' ? undefined : undefined, // Browser handles this automatically
  httpsAgent: typeof window === 'undefined' ? undefined : undefined,
  // Max redirects
  maxRedirects: 5,
  // Validate status
  validateStatus: (status) => status >= 200 && status < 300,
})

interface SearchResult {
  case_name: string
  citation: string
  relevance_score: number
  snippet: string
  court: string
  date: string
  url?: string
  collection?: string
  rerank_score?: number
  semantic_score?: number
  bm25_score?: number
  citations?: Array<{ text: string; link?: string }>
  full_text?: string
}

interface SearchResponse {
  answer: string
  sources: Array<{
    content: string
    score: number
    metadata: {
      title: string
      collection: string
      court?: string
      date?: string
      citation?: string
      url?: string
    }
  }>
  metadata: {
    total_searched: number
    query_time: number
    collection: string
  }
}

export default function Home() {
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searchTime, setSearchTime] = useState<number | null>(null)
  const [queryHistory, setQueryHistory] = useState<string[]>([])
  const [expandedSources, setExpandedSources] = useState<Record<number, boolean>>({})
  const [showSidebar, setShowSidebar] = useState(false)

  // Settings
  const [collection, setCollection] = useState('both')
  const [limit, setLimit] = useState(5)
  const [showSources, setShowSources] = useState(true)
  
  // Advanced Filters
  const [useHybrid, setUseHybrid] = useState(true)
  const [useReranking, setUseReranking] = useState(true)
  const [extractCitations, setExtractCitations] = useState(true)

  // Get API URL - Next.js bakes NEXT_PUBLIC_* vars at build time
  // For production, this should be set as build arg in Dockerfile
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  
  // Debug: Log the API URL being used (only in browser console)
  useEffect(() => {
    console.log('🔍 Frontend API URL:', apiUrl)
    console.log('🔍 Environment variable:', process.env.NEXT_PUBLIC_API_URL)
  }, [apiUrl])

  // Load query history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('lawscout_query_history')
    if (saved) {
      setQueryHistory(JSON.parse(saved))
    }
  }, [])

  // Save query history to localStorage
  const saveToHistory = (q: string) => {
    if (!q.trim()) return; // Don't save empty queries
    setQueryHistory(prev => {
      const newHistory = [q, ...prev.filter(item => item !== q)].slice(0, 20); // Keep last 20 unique queries
      localStorage.setItem('lawscout_query_history', JSON.stringify(newHistory));
      return newHistory;
    });
  }

  // Delete a specific history item
  const deleteHistoryItem = (index: number) => {
    setQueryHistory(prev => {
      const newHistory = prev.filter((_, i) => i !== index)
      localStorage.setItem('lawscout_query_history', JSON.stringify(newHistory))
      return newHistory
    })
  }

  // Clear all history
  const clearHistory = () => {
    setQueryHistory([])
    localStorage.removeItem('lawscout_query_history')
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setAnswer('')
    setResults([])
    const startTime = Date.now()
    
      try {
      // Use optimized axios instance with connection pooling
      const response = await apiClient.post<SearchResponse>(`${apiUrl}/api/v1/search`, {
        query: query,
        collection: collection,
        limit: limit,
        use_hybrid: useHybrid,
        use_reranking: useReranking,
        extract_citations: extractCitations
      })
      
      saveToHistory(query)
      setAnswer(response.data.answer || 'No answer generated')
      
      const mappedResults = (response.data.sources || []).map((source: any, idx: number) => ({
        case_name: source.metadata?.title || 'Unknown',
        citation: source.metadata?.citation || 'N/A',
        relevance_score: source.score || 0,
        snippet: source.content?.substring(0, 300) || '',
        full_text: source.content || '',
        court: source.metadata?.court || 'N/A',
        date: source.metadata?.date || 'N/A',
        url: source.metadata?.url,
        collection: source.metadata?.collection || 'unknown',
        rerank_score: source.rerank_score,
        semantic_score: source.semantic_score,
        bm25_score: source.bm25_score,
        citations: source.citations || []
      }))
      
      setResults(mappedResults)
      setSearchTime(Date.now() - startTime)
      
      if (mappedResults.length > 0) {
        setExpandedSources({ 0: true })
      }
    } catch (err: any) {
      // Enhanced error logging for debugging
      console.error('🔴 Search error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        url: `${apiUrl}/api/v1/search`,
        code: err.code,
        config: err.config
      })
      
      // More detailed error message
      let errorMsg = 'Search failed. Please try again.'
      if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail
      } else if (err.message) {
        errorMsg = `Network error: ${err.message}`
      } else if (err.code === 'ERR_NETWORK' || err.code === 'ECONNREFUSED') {
        errorMsg = `Cannot connect to backend at ${apiUrl}. Please check the API URL configuration.`
      }
      
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery)
  }

  const handleHistoryClick = (histQuery: string) => {
    setQuery(histQuery)
  }

  const handleQuickSearch = (quickQuery: string) => {
    setQuery(quickQuery)
  }

  const toggleSource = (index: number) => {
    setExpandedSources(prev => ({ ...prev, [index]: !prev[index] }))
  }

  const exportResults = () => {
    const exportContent = `# LawScout AI Research Results

Query: ${query}
Date: ${new Date().toISOString()}
Collection: ${collection}
Search Time: ${searchTime ? (searchTime / 1000).toFixed(2) + 's' : 'N/A'}

## Answer
${answer}

## Sources
${results.map((source, i) => `
### Source ${i + 1}
Title: ${source.case_name}
Relevance: ${(source.relevance_score * 100).toFixed(1)}%
Citation: ${source.citation}
Court: ${source.court}
Date: ${source.date}
Content: ${source.full_text || source.snippet}
`).join('\n')}
`

    const blob = new Blob([exportContent], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `lawscout_research_${query.substring(0, 30).replace(/\s+/g, '_')}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const exampleQueries = [
    "What are the requirements for breach of contract?",
    "Explain qualified immunity for police officers",
    "What is the standard for summary judgment?",
    "Define negligence in tort law",
    "What are Miranda rights?",
    "How do I draft a motion for judgment on the pleadings?",
    "What must be included in a Memorandum of Points and Authorities?"
  ]

  return (
    <div className="min-h-screen bg-harvey-dark flex">
      {/* Sidebar */}
      {showSidebar && (
      <Sidebar
        collection={collection}
        setCollection={setCollection}
        limit={limit}
        setLimit={setLimit}
        showSources={showSources}
        setShowSources={setShowSources}
        useHybrid={useHybrid}
        setUseHybrid={setUseHybrid}
        useReranking={useReranking}
        setUseReranking={setUseReranking}
        extractCitations={extractCitations}
        setExtractCitations={setExtractCitations}
        queryHistory={queryHistory}
        onHistoryClick={handleHistoryClick}
        onQuickSearch={handleQuickSearch}
        onDeleteHistory={deleteHistoryItem}
        onClearHistory={clearHistory}
      />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Navigation - Harvey.ai style */}
        <nav className="bg-harvey-dark border-b border-gray-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-20">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setShowSidebar(!showSidebar)}
                  className="text-white hover:text-gray-300 transition-colors p-2 hover:bg-gray-900 rounded-md"
                  title={showSidebar ? "Hide sidebar" : "Show sidebar"}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {showSidebar ? (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    )}
                  </svg>
                </button>
                <h1 className="text-2xl font-serif-heading text-white">LawScout AI</h1>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content - Harvey.ai style */}
        <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-6xl md:text-7xl font-serif-heading text-white mb-6 leading-tight">
            AI-Powered<br />Legal Research
          </h1>
          <p className="text-lg md:text-xl text-gray-400 mb-10 font-light max-w-2xl mx-auto">
            Master legal concepts and procedures, draft precise documents, and conduct thorough analysis — all for free to start.
          </p>
        </div>

        {/* Search Form - Harvey.ai style */}
        <div className="mb-12">
          <form onSubmit={handleSearch} className="space-y-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a legal question"
                className="flex-1 px-6 py-4 text-base border border-gray-700 rounded-md bg-harvey-dark text-white placeholder-gray-500 focus:border-white focus:outline-none transition-colors"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="px-10 py-4 bg-white text-harvey-dark font-medium rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Searching...
                  </span>
                ) : (
                  'Search'
                )}
              </button>
            </div>
          </form>

          {/* Example Queries - Harvey.ai style */}
          <div className="mt-8">
            <p className="text-sm text-gray-500 mb-4 text-center">Example queries:</p>
            <div className="flex flex-wrap gap-3 justify-center">
              {exampleQueries.slice(0, 5).map((example, idx) => (
                <button
                  key={idx}
                  onClick={() => handleExampleClick(example)}
                  className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors border border-gray-800 hover:border-gray-700 rounded-md"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-950 border border-red-900 rounded-md text-red-200 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Answer Section */}
        {answer && (
          <div className="mb-12 p-8 bg-harvey-dark border border-gray-800 rounded-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-serif-heading text-white">Answer</h2>
              {results.length > 0 && (
                <button
                  onClick={exportResults}
                  className="px-5 py-2 bg-white text-harvey-dark hover:bg-gray-100 rounded-md transition-colors text-sm font-medium"
                >
                  📥 Download Results
                </button>
              )}
            </div>
            <div className="prose max-w-none">
              <p className="text-gray-300 leading-relaxed whitespace-pre-wrap font-light">{answer}</p>
            </div>
          </div>
        )}

        {/* Sources Section */}
        {showSources && results.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-serif-heading text-white">Sources ({results.length})</h2>
              <button
                onClick={exportResults}
                className="px-5 py-2 bg-white text-harvey-dark hover:bg-gray-100 rounded-md transition-colors text-sm font-medium"
              >
                Export Results
              </button>
            </div>

            <div className="space-y-3">
              {results.map((result, idx) => (
                <div key={idx} className="bg-harvey-dark rounded-md border border-gray-800 overflow-hidden">
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="text-lg font-serif-heading text-white mb-2">
                          {result.url ? (
                            <a
                              href={result.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="hover:text-gray-300 transition-colors underline"
                              onClick={(e) => e.stopPropagation()}
                            >
                              {result.case_name}
                            </a>
                          ) : (
                            result.case_name
                          )}
                        </h3>
                        <div className="flex flex-wrap gap-4 text-sm text-gray-500 font-light">
                          <span>Score: {(result.relevance_score * 100).toFixed(1)}%</span>
                          {result.url ? (
                            <a
                              href={result.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-gray-400 hover:text-white transition-colors underline"
                              onClick={(e) => e.stopPropagation()}
                            >
                              {result.citation}
                            </a>
                          ) : (
                            <span>{result.citation}</span>
                          )}
                          <span>{result.court}</span>
                          <span>{result.date}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => toggleSource(idx)}
                        className="text-gray-600 hover:text-white ml-4 text-xl transition-colors"
                      >
                        {expandedSources[idx] ? '−' : '+'}
                      </button>
                    </div>
                    {result.url && (
                      <div className="mt-3">
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-sm text-white hover:text-gray-300 font-normal underline transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          View Full Source →
                        </a>
                      </div>
                    )}
                  </div>

                  {expandedSources[idx] && (
                    <div className="px-6 pb-6 border-t border-gray-800">
                      <div className="mt-6">
                        <p className="text-sm text-gray-400 leading-relaxed font-light">
                          {(result.full_text || result.snippet).substring(0, 1000)}
                          {(result.full_text || result.snippet).length > 1000 && '...'}
                        </p>
                      </div>
                      {result.url && (
                        <div className="mt-6">
                          <a
                            href={result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-sm text-white hover:text-gray-300 font-normal underline transition-colors"
                          >
                            View Full Source →
                          </a>
                        </div>
                      )}
                      {result.citations && result.citations.length > 0 && (
                        <div className="mt-6 pt-6 border-t border-gray-800">
                          <p className="text-xs text-gray-500 mb-3 font-light">Citations Found:</p>
                          <div className="space-y-2">
                            {result.citations.map((citation: any, cIdx: number) => (
                              <div key={cIdx}>
                                {citation.link ? (
                                  <a
                                    href={citation.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-sm text-white hover:text-gray-300 underline transition-colors"
                                  >
                                    {citation.text}
                                  </a>
                                ) : (
                                  <span className="text-sm text-gray-400">{citation.text}</span>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metrics */}
        {results.length > 0 && (
          <div className="mb-12 p-8 bg-harvey-dark rounded-md border border-gray-800">
            <h3 className="text-lg font-serif-heading text-white mb-6">Search Metrics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <p className="text-xs text-gray-500 mb-2 font-light">Documents Searched</p>
                <p className="text-2xl font-serif-heading text-white">276,970</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-2 font-light">Relevant Sources</p>
                <p className="text-2xl font-serif-heading text-white">{results.length}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-2 font-light">Top Match Score</p>
                <p className="text-2xl font-serif-heading text-white">
                  {results[0] ? (results[0].relevance_score * 100).toFixed(1) + '%' : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-2 font-light">Search Time</p>
                <p className="text-2xl font-serif-heading text-white">
                  {searchTime ? (searchTime / 1000).toFixed(2) + 's' : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && results.length === 0 && !answer && !error && (
          <div className="text-center py-20">
            <h3 className="text-2xl font-serif-heading text-white mb-3">
              Ready to Search
            </h3>
            <p className="text-gray-500 font-light">
              Enter a legal question above or click one of the example queries
            </p>
          </div>
        )}

        {/* Legal Notice */}
        <div className="mt-16 pt-8 border-t border-gray-800">
          <p className="text-sm text-gray-500 text-center font-light">
            This is a research demonstration only – not legal advice. Always verify with primary sources and consult qualified attorneys.
          </p>
        </div>
      </main>

        {/* Footer */}
        <footer className="border-t border-gray-800 mt-20 bg-harvey-dark">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="flex justify-center space-x-8 text-sm text-gray-500">
              <a href="#" className="hover:text-white transition-colors font-light">Support</a>
              <a href="#" className="hover:text-white transition-colors font-light">Terms</a>
              <a href="#" className="hover:text-white transition-colors font-light">Privacy</a>
              <a href="https://www.courtlistener.com/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors font-light">
                US Courts & Case Law
              </a>
            </div>
            <div className="mt-8 text-center text-sm text-gray-600 font-light">
              <p>Legal case opinions sourced from <a href="https://www.courtlistener.com/" target="_blank" rel="noopener noreferrer" className="text-white hover:underline">CourtListener</a>, a project of the <a href="https://free.law/" target="_blank" rel="noopener noreferrer" className="text-white hover:underline">Free Law Project</a>.</p>
              <p className="mt-2">Contract data from the <a href="https://www.atticusprojectai.org/cuad" target="_blank" rel="noopener noreferrer" className="text-white hover:underline">CUAD Dataset</a>.</p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
