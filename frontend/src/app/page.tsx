'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import Sidebar from '@/components/Sidebar'
import { useAuth } from '@/contexts/AuthContext'
import UpgradeBanner from '@/components/UpgradeBanner'
import AuthStatus from '@/components/AuthStatus'

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
  const { user, token, checkLimit, refreshUser, loading: authLoading } = useAuth()
  const router = useRouter()
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
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.lawscoutai.com'

  // Debug: Log the API URL being used (only in browser console)
  useEffect(() => {
    console.log('🔍 Frontend API URL:', apiUrl)
    console.log('🔍 Environment variable:', process.env.NEXT_PUBLIC_API_URL)
  }, [apiUrl])

  // Refresh auth state on mount if token exists but user is missing
  // This fixes the issue where OAuth callback redirects before state propagates
  useEffect(() => {
    const checkAndRefreshAuth = async () => {
      if (typeof window === 'undefined') return

      const storedToken = localStorage.getItem('lawscout_auth_token')
      if (storedToken && !user && !loading) {
        // Token exists but user state not loaded, refresh it
        try {
          await refreshUser()
        } catch (error) {
          console.error('Failed to refresh auth state:', error)
        }
      }
    }

    // Small delay to let AuthContext initialize first
    const timer = setTimeout(() => {
      checkAndRefreshAuth()
    }, 100)

    return () => clearTimeout(timer)
  }, [user, loading, refreshUser])

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

  const handleSearch = async (e: React.FormEvent, searchQuery?: string) => {
    e.preventDefault()
    const queryToSearch = searchQuery || query
    if (!queryToSearch.trim()) return

    // Wait for auth to finish loading and refresh if needed
    if (authLoading || (!user && typeof window !== 'undefined')) {
      const storedToken = localStorage.getItem('lawscout_auth_token')
      if (storedToken && !user) {
        // Token exists but user state not loaded - refresh it
        try {
          await refreshUser()
        } catch (err) {
          console.error('Failed to refresh auth state:', err)
        }
      }
      // Small delay to let state update
      await new Promise(resolve => setTimeout(resolve, 200))
    }

    // Check authentication - use localStorage as fallback to avoid race conditions
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('lawscout_auth_token') : null
    const storedUser = typeof window !== 'undefined' ? (() => {
      try {
        const userStr = localStorage.getItem('lawscout_user')
        return userStr ? JSON.parse(userStr) : null
      } catch {
        return null
      }
    })() : null
    const currentToken = token || storedToken
    const currentUser = user || storedUser

    if (!currentUser || !currentToken) {
      setError('Please sign in or create an account to search. Sign up is free!')
      return
    }

    // Check search limit (use currentToken)
    try {
      // Use checkLimit which uses token from context, or call API directly with currentToken
      const limit = await checkLimit()
      if (!limit.can_search) {
        setError(limit.message)
        return
      }
    } catch {
      // If checkLimit fails, try direct API call with currentToken
      if (currentToken) {
        try {
          const res = await fetch(`${apiUrl}/api/auth/search/check-limit`, {
            headers: {
              'Authorization': `Bearer ${currentToken}`,
              'Content-Type': 'application/json'
            }
          })
          if (res.ok) {
            const limitData = await res.json()
            if (!limitData.can_search) {
              setError(limitData.message)
              return
            }
          }
        } catch (apiErr) {
          console.error('Failed to check limit:', apiErr)
          // Continue anyway - let backend handle auth
        }
      } else {
        setError('Unable to verify search limit. Please try again.')
        return
      }
    }

    setLoading(true)
    setError('')
    setAnswer('')
    setResults([])
    const startTime = Date.now()

    try {
      // Use optimized axios instance with connection pooling
      // Use currentToken (from state or localStorage) to ensure we have the token
      const response = await apiClient.post<SearchResponse>(`${apiUrl}/api/v1/search`, {
        query: queryToSearch,
        collection: collection,
        limit: limit,
        use_hybrid: useHybrid,
        use_reranking: useReranking,
        extract_citations: extractCitations
      }, {
        headers: {
          'Authorization': `Bearer ${currentToken}`
        }
      })

      saveToHistory(queryToSearch)
      setAnswer(response.data.answer || 'No answer generated')

      const mappedResults = (response.data.sources || []).map((source: any) => ({
        case_name: source.metadata?.title || source.metadata?.name || 'Unknown',
        citation: source.metadata?.citation || null,
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

      // Usage is enforced and recorded atomically by /api/v1/search.
      // Refresh the account so the remaining-search count updates in the UI.
      if (currentUser && currentToken) {
        try {
          await refreshUser()
        } catch (refreshError) {
          console.error('Failed to refresh search usage:', refreshError)
        }
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

  const handleExampleClick = async (exampleQuery: string) => {
    // Wait for auth to finish loading and refresh if needed
    if (authLoading || (!user && typeof window !== 'undefined')) {
      const storedToken = localStorage.getItem('lawscout_auth_token')
      if (storedToken && !user) {
        try {
          await refreshUser()
        } catch (err) {
          console.error('Failed to refresh user during example click:', err)
        }
      }
      await new Promise(resolve => setTimeout(resolve, 200))
    }

    // Check authentication - use localStorage as fallback
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('lawscout_auth_token') : null
    const storedUser = typeof window !== 'undefined' ? (() => {
      try {
        const userStr = localStorage.getItem('lawscout_user')
        return userStr ? JSON.parse(userStr) : null
      } catch {
        return null
      }
    })() : null
    const currentToken = token || storedToken
    const currentUser = user || storedUser

    if (!currentUser || !currentToken) {
      setError('Please sign in or create an account to search. Sign up is free!')
      return
    }

    setQuery(exampleQuery)
    // Auto-trigger search with the example query
    const syntheticEvent = {
      preventDefault: () => {},
    } as React.FormEvent
    handleSearch(syntheticEvent, exampleQuery)
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
        <nav className="bg-harvey-dark border-b border-gray-800 relative z-20">
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
                <Link href="/" className="text-2xl font-serif-heading text-white hover:text-gray-300 transition-colors">
                  LawScout AI
                </Link>
              </div>
              <AuthStatus />
            </div>
          </div>
        </nav>

        {/* Main Content - Harvey.ai style */}
        <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full">
        {/* Upgrade Banner */}
        <UpgradeBanner />

        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-6xl md:text-7xl font-serif-heading text-white mb-6 leading-tight">
            AI-Powered<br />Legal Research
          </h1>
          <p className="text-lg md:text-xl text-gray-400 mb-10 font-light max-w-2xl mx-auto">
            Master legal concepts and procedures, draft precise documents, and conduct thorough analysis — all for free to start.
          </p>
        </div>

        {/* Stats Banner */}
        <section className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 py-8 border-y border-gray-800 mb-12">
          <div className="max-w-6xl mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-4xl font-bold text-blue-400 mb-1">276,970+</div>
                <div className="text-sm text-gray-400">Legal Documents</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-blue-400 mb-1">15</div>
                <div className="text-sm text-gray-400">Free Searches</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-blue-400 mb-1">&lt;2s</div>
                <div className="text-sm text-gray-400">Response Time</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-blue-400 mb-1">$29/mo</div>
                <div className="text-sm text-gray-400">Pro (vs $100+ competitors)</div>
              </div>
            </div>
          </div>
        </section>

        {/* Search Form - Harvey.ai style */}
        <div className="mb-12">
          <form onSubmit={handleSearch} className="space-y-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={user ? "Ask a legal question" : "Sign in to search legal documents"}
                className="flex-1 px-6 py-4 text-base border border-gray-700 rounded-md bg-harvey-dark text-white placeholder-gray-500 focus:border-white focus:outline-none transition-colors"
                disabled={loading || !user}
              />
              <button
                type="submit"
                disabled={loading || !query.trim() || !user}
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

          {/* Example Queries - Only show expandable section, not redundant buttons */}
          {!user && (
            <div className="mt-8 p-8 bg-harvey-dark border border-gray-800 rounded-md text-center">
              <div className="text-5xl mb-4">🔒</div>
              <h3 className="text-2xl font-bold mb-2 text-white">Sign in required to search</h3>
              <p className="text-gray-400 mb-6">
                Create a free account to access our legal research database
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
                <button
                  onClick={() => router.push('/register')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-bold transition cursor-pointer"
                >
                  Sign Up Free - 15 Searches
                </button>
                <button
                  onClick={() => router.push('/login')}
                  className="bg-gray-700 hover:bg-gray-600 text-white px-8 py-3 rounded-lg font-bold transition cursor-pointer"
                >
                  Sign In
                </button>
              </div>

              {/* Quick Links */}
              <div className="flex flex-wrap items-center justify-center gap-4 text-sm mb-6">
                <a href="#examples" className="text-blue-400 hover:underline flex items-center gap-1 cursor-pointer">
                  👀 See example searches
                </a>
                <span className="text-gray-600">•</span>
                <a href="#how-it-works" className="text-blue-400 hover:underline flex items-center gap-1 cursor-pointer">
                  🔍 How it works
                </a>
                <span className="text-gray-600">•</span>
                <Link href="/support" className="text-blue-400 hover:underline flex items-center gap-1">
                  ❓ Full FAQ
                </Link>
              </div>

              {/* Quick Stats */}
              <div className="pt-6 border-t border-gray-700">
                <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-400">
                  <span>✓ 276,970+ legal documents</span>
                  <span>✓ AI-powered search</span>
                  <span>✓ Instant citations</span>
                  <span>✓ $29/mo Pro tier</span>
                </div>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-950 border border-red-900 rounded-md text-red-200 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Expandable Content Sections - Show for non-authenticated users */}
        {!user && (
          <div className="max-w-6xl mx-auto space-y-6 mb-12">

            {/* Example Queries - OPEN BY DEFAULT */}
            <details id="examples" className="bg-harvey-dark rounded-lg border border-gray-800 p-6 group" open>
              <summary className="text-xl font-bold cursor-pointer flex items-center gap-2 list-none">
                <span className="text-2xl">💡</span>
                <span>See What You Can Search For</span>
                <span className="text-sm text-gray-400 ml-auto group-open:hidden">(click to expand)</span>
                <span className="text-sm text-gray-400 ml-auto hidden group-open:inline">(click to collapse)</span>
              </summary>

              <div className="mt-6">
                <p className="text-gray-400 mb-6 text-center">
                  Real examples of legal research queries you can run
                </p>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all cursor-pointer transform hover:-translate-y-1">
                    <p className="text-blue-400 text-sm mb-2 font-mono">Case Law</p>
                    <p className="font-semibold text-white">"What is qualified immunity?"</p>
                  </div>

                  <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all cursor-pointer transform hover:-translate-y-1">
                    <p className="text-blue-400 text-sm mb-2 font-mono">Constitutional Law</p>
                    <p className="font-semibold text-white">"Fourth Amendment search and seizure exceptions"</p>
                  </div>

                  <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all cursor-pointer transform hover:-translate-y-1">
                    <p className="text-blue-400 text-sm mb-2 font-mono">Contract Law</p>
                    <p className="font-semibold text-white">"What makes a contract legally binding?"</p>
                  </div>

                  <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all cursor-pointer transform hover:-translate-y-1">
                    <p className="text-blue-400 text-sm mb-2 font-mono">Civil Procedure</p>
                    <p className="font-semibold text-white">"Summary judgment standard in federal court"</p>
                  </div>

                  <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all cursor-pointer transform hover:-translate-y-1">
                    <p className="text-blue-400 text-sm mb-2 font-mono">Criminal Law</p>
                    <p className="font-semibold text-white">"Miranda rights exceptions and waivers"</p>
                  </div>

                  <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all cursor-pointer transform hover:-translate-y-1">
                    <p className="text-blue-400 text-sm mb-2 font-mono">Employment Law</p>
                    <p className="font-semibold text-white">"At-will employment termination rules"</p>
                  </div>
                </div>

                <div className="mt-6 text-center">
                  <Link href="/support" className="text-blue-400 hover:underline text-sm">
                    View more examples and full FAQ →
                  </Link>
                </div>
              </div>
            </details>

            {/* How It Works */}
            <details id="how-it-works" className="bg-harvey-dark rounded-lg border border-gray-800 p-6 group">
              <summary className="text-xl font-bold cursor-pointer flex items-center gap-2 list-none">
                <span className="text-2xl">🔍</span>
                <span>How It Works</span>
                <span className="text-sm text-gray-400 ml-auto group-open:hidden">(click to expand)</span>
                <span className="text-sm text-gray-400 ml-auto hidden group-open:inline">(click to collapse)</span>
              </summary>

              <div className="grid md:grid-cols-3 gap-8 mt-6">
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">
                    🔍
                  </div>
                  <h3 className="text-lg font-bold mb-2 text-white">1. Ask Your Question</h3>
                  <p className="text-sm text-gray-400">
                    Search our database of 276,970+ legal documents including case law, contracts, and legal opinions
                  </p>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">
                    🤖
                  </div>
                  <h3 className="text-lg font-bold mb-2 text-white">2. AI Analyzes</h3>
                  <p className="text-sm text-gray-400">
                    Our AI searches relevant cases, extracts key points, and synthesizes accurate answers with citations
                  </p>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">
                    ⚡
                  </div>
                  <h3 className="text-lg font-bold mb-2 text-white">3. Get Instant Results</h3>
                  <p className="text-sm text-gray-400">
                    Receive comprehensive answers in seconds with case citations and relevant legal precedents
                  </p>
                </div>
              </div>
            </details>

            {/* Comparison Table */}
            <details className="bg-harvey-dark rounded-lg border border-gray-800 p-6 group">
              <summary className="text-xl font-bold cursor-pointer flex items-center gap-2 list-none">
                <span className="text-2xl">⚖️</span>
                <span>Why Choose LawScout AI?</span>
                <span className="text-sm text-gray-400 ml-auto group-open:hidden">(click to expand)</span>
                <span className="text-sm text-gray-400 ml-auto hidden group-open:inline">(click to collapse)</span>
              </summary>

              <div className="mt-6">
                <p className="text-center text-gray-400 mb-6">
                  Professional legal research without the enterprise price tag
                </p>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="py-4 px-4 text-white">Feature</th>
                        <th className="py-4 px-3 text-center text-gray-400">Westlaw</th>
                        <th className="py-4 px-3 text-center text-gray-400">LexisNexis</th>
                        <th className="py-4 px-3 text-center text-gray-400">ChatGPT Plus</th>
                        <th className="py-4 px-3 text-center bg-blue-900/30 rounded-t-lg">
                          <span className="text-blue-400 font-bold">LawScout AI</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-800">
                        <td className="py-4 px-4 font-semibold text-white">Monthly Cost</td>
                        <td className="py-4 px-3 text-center text-gray-400">$100-500</td>
                        <td className="py-4 px-3 text-center text-gray-400">$100-400</td>
                        <td className="py-4 px-3 text-center text-gray-400">$20</td>
                        <td className="py-4 px-3 text-center bg-blue-900/30">
                          <span className="text-blue-400 font-bold">$0-29</span>
                        </td>
                      </tr>
                      <tr className="border-b border-gray-800">
                        <td className="py-4 px-4 font-semibold text-white">Legal Database</td>
                        <td className="py-4 px-3 text-center text-white">✅ Millions</td>
                        <td className="py-4 px-3 text-center text-white">✅ Millions</td>
                        <td className="py-4 px-3 text-center text-gray-400">❌ General</td>
                        <td className="py-4 px-3 text-center bg-blue-900/30">
                          <span className="text-blue-400 font-bold">✅ 276k+</span>
                        </td>
                      </tr>
                      <tr className="border-b border-gray-800">
                        <td className="py-4 px-4 font-semibold text-white">AI Analysis</td>
                        <td className="py-4 px-3 text-center text-gray-400">⚠️ Limited</td>
                        <td className="py-4 px-3 text-center text-gray-400">⚠️ Limited</td>
                        <td className="py-4 px-3 text-center text-white">✅ Yes</td>
                        <td className="py-4 px-3 text-center bg-blue-900/30">
                          <span className="text-blue-400 font-bold">✅ Advanced</span>
                        </td>
                      </tr>
                      <tr className="border-b border-gray-800">
                        <td className="py-4 px-4 font-semibold text-white">Free Tier</td>
                        <td className="py-4 px-3 text-center text-gray-400">❌ No</td>
                        <td className="py-4 px-3 text-center text-gray-400">❌ No</td>
                        <td className="py-4 px-3 text-center text-gray-400">⚠️ Limited</td>
                        <td className="py-4 px-3 text-center bg-blue-900/30">
                          <span className="text-blue-400 font-bold">✅ 15 searches</span>
                        </td>
                      </tr>
                      <tr>
                        <td className="py-4 px-4 font-semibold text-white">Best For</td>
                        <td className="py-4 px-3 text-center text-xs text-gray-400">Large firms</td>
                        <td className="py-4 px-3 text-center text-xs text-gray-400">Enterprises</td>
                        <td className="py-4 px-3 text-center text-xs text-gray-400">General AI</td>
                        <td className="py-4 px-3 text-center bg-blue-900/30 text-xs rounded-b-lg">
                          <span className="text-blue-400 font-bold">Students, Solos, Paralegals</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <p className="mt-6 text-center text-sm text-gray-400">
                  💰 Save 70-85% compared to traditional legal research tools
                </p>
              </div>
            </details>

            {/* Quick FAQ */}
            <details className="bg-harvey-dark rounded-lg border border-gray-800 p-6 group">
              <summary className="text-xl font-bold cursor-pointer flex items-center gap-2 list-none">
                <span className="text-2xl">❓</span>
                <span>Common Questions</span>
                <span className="text-sm text-gray-400 ml-auto group-open:hidden">(click to expand)</span>
                <span className="text-sm text-gray-400 ml-auto hidden group-open:inline">(click to collapse)</span>
              </summary>

              <div className="space-y-6 mt-6">
                <div>
                  <p className="font-bold mb-2 text-blue-400">Is this legal advice?</p>
                  <p className="text-sm text-gray-400">
                    No. LawScout AI is a research tool, not a substitute for professional legal counsel. Always consult qualified attorneys for legal matters affecting you.
                  </p>
                </div>

                <div>
                  <p className="font-bold mb-2 text-blue-400">What happens after 15 free searches?</p>
                  <p className="text-sm text-gray-400">
                    You'll be prompted to upgrade to Pro ($29/month) for unlimited searches. Your account remains active, but you won't be able to perform new searches until you upgrade.
                  </p>
                </div>

                <div>
                  <p className="font-bold mb-2 text-blue-400">How accurate are the search results?</p>
                  <p className="text-sm text-gray-400">
                    Our AI searches through 276,970+ verified legal documents using advanced vector search. While we strive for accuracy, always verify information with primary sources and consult qualified attorneys.
                  </p>
                </div>

                <div>
                  <p className="font-bold mb-2 text-blue-400">Can I use this for commercial purposes?</p>
                  <p className="text-sm text-gray-400">
                    Yes, both Free and Pro tiers can be used for commercial legal research. However, you must comply with our Terms of Service.
                  </p>
                </div>

                <div>
                  <p className="font-bold mb-2 text-blue-400">What's included in the Pro tier?</p>
                  <p className="text-sm text-gray-400">
                    Pro tier (coming soon) includes unlimited searches, priority support, advanced AI features, and export capabilities for just $29/month.
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-700 text-center">
                <Link href="/support" className="text-blue-400 hover:underline text-sm">
                  See all 10 FAQs and contact support →
                </Link>
              </div>
            </details>
          </div>
        )}

        {/* Expandable Sections for Authenticated Users (when no results) */}
        {user && !loading && results.length === 0 && !answer && !error && (
          <div className="max-w-6xl mx-auto space-y-6 mb-12">
            <details id="examples" className="bg-harvey-dark rounded-lg border border-gray-800 p-6 group" open>
              <summary className="text-xl font-bold cursor-pointer flex items-center gap-2 list-none">
                <span className="text-2xl">💡</span>
                <span>Example Queries</span>
                <span className="text-sm text-gray-400 ml-auto group-open:hidden">(click to expand)</span>
                <span className="text-sm text-gray-400 ml-auto hidden group-open:inline">(click to collapse)</span>
              </summary>

              <div className="mt-6">
                <p className="text-gray-400 mb-6 text-center">
                  Click any example to search immediately
                </p>

                <div className="grid md:grid-cols-2 gap-4">
                  {exampleQueries.slice(0, 6).map((example, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleExampleClick(example)}
                      className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all cursor-pointer transform hover:-translate-y-1 text-left"
                    >
                      <p className="text-blue-400 text-sm mb-2 font-mono">Example Query</p>
                      <p className="font-semibold text-white">{example}</p>
                    </button>
                  ))}
                </div>
              </div>
            </details>
          </div>
        )}

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
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                className="text-gray-300 leading-relaxed font-light"
                components={{
                  // Style links to match the site theme
                  a: ({node: _node, ...props}) => (
                    <a
                      {...props}
                      className="text-blue-400 hover:text-blue-300 underline transition-colors"
                      target="_blank"
                      rel="noopener noreferrer"
                    />
                  ),
                  // Style lists
                  ul: ({node: _node, ...props}) => (
                    <ul {...props} className="list-disc list-inside space-y-2 my-4" />
                  ),
                  ol: ({node: _node, ...props}) => (
                    <ol {...props} className="list-decimal list-inside space-y-2 my-4" />
                  ),
                  // Style paragraphs
                  p: ({node: _node, ...props}) => (
                    <p {...props} className="mb-4" />
                  ),
                  // Style strong/bold
                  strong: ({node: _node, ...props}) => (
                    <strong {...props} className="font-semibold text-white" />
                  ),
                }}
              >
                {answer}
              </ReactMarkdown>
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
                          {result.relevance_score > 0 ? (
                            <span>Score: {(result.relevance_score * 100).toFixed(1)}%</span>
                          ) : (
                            <span className="text-gray-600">Score: Low relevance</span>
                          )}
                          {result.citation ? (
                            result.url ? (
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
                            )
                          ) : (
                            <span className="text-gray-600">No citation</span>
                          )}
                          {result.court && result.court !== 'N/A' && (
                            <span>{result.court}</span>
                          )}
                          {result.date && result.date !== 'N/A' && (
                            <span>{result.date}</span>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => toggleSource(idx)}
                        className="text-gray-600 hover:text-white ml-4 text-xl transition-colors"
                      >
                        {expandedSources[idx] ? '−' : '+'}
                      </button>
                    </div>
                    <div className="mt-3 flex items-center gap-4">
                      {result.url && (
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-sm text-white hover:text-gray-300 font-normal underline transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                          {result.url.includes('.pdf') || result.url.includes('pdf') ? 'View PDF' : 'View Full Source'}
                        </a>
                      )}
                      {result.citation && !result.url && (
                        <span className="text-sm text-gray-500 font-light">Citation: {result.citation}</span>
                      )}
                    </div>
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
                          <p className="text-xs text-gray-500 mb-3 font-light uppercase tracking-wide">Citations Found in Text:</p>
                          <div className="space-y-2">
                            {result.citations.map((citation: any, cIdx: number) => (
                              <div key={cIdx} className="flex items-center gap-2">
                                {citation.link ? (
                                  <a
                                    href={citation.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 underline transition-colors"
                                  >
                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                    </svg>
                                    {citation.text}
                                  </a>
                                ) : (
                                  <span className="text-sm text-gray-400">{citation.text}</span>
                                )}
                                {citation.type && (
                                  <span className="text-xs text-gray-600 font-light">({citation.type})</span>
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

        {/* Empty State - Only show for authenticated users */}
        {!loading && results.length === 0 && !answer && !error && user && (
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

        {/* Final CTA - Only for non-authenticated users */}
        {!user && (
          <section className="max-w-4xl mx-auto px-4 py-16">
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-10 rounded-2xl text-center">
              <h2 className="text-3xl font-bold mb-3 text-white">
                Ready to Start Your Legal Research?
              </h2>
              <p className="text-xl mb-6 text-blue-100">
                Join hundreds of students, paralegals, and practitioners
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
                <button
                  onClick={() => router.push('/register')}
                  className="bg-white text-blue-600 px-10 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition shadow-lg cursor-pointer"
                >
                  Sign Up Free - Get 15 Searches
                </button>
                <button
                  onClick={() => router.push('/login')}
                  className="bg-transparent border-2 border-white text-white px-10 py-4 rounded-lg font-bold text-lg hover:bg-white/10 transition cursor-pointer"
                >
                  Sign In
                </button>
              </div>

              <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-blue-100">
                <span>✓ No credit card required</span>
                <span>•</span>
                <span>✓ 30 seconds to sign up</span>
                <span>•</span>
                <span>✓ Start searching immediately</span>
              </div>
            </div>
          </section>
        )}
      </main>

        {/* Footer */}
        <footer className="border-t border-gray-800 mt-20 bg-harvey-dark">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="flex justify-center space-x-8 text-sm text-gray-500">
              <Link href="/support" className="hover:text-white transition-colors font-light">Support</Link>
              <Link href="/terms" className="hover:text-white transition-colors font-light">Terms</Link>
              <Link href="/privacy" className="hover:text-white transition-colors font-light">Privacy</Link>
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
