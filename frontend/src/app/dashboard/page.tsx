'use client'

import { useAuth } from '@/contexts/AuthContext'
import Link from 'next/link'
import { useEffect, useState } from 'react'

export default function DashboardPage() {
  const { user, loading } = useAuth()
  const [stats, setStats] = useState({
    totalSearches: 0,
    searchesThisMonth: 0,
    averageResults: 0
  })

  useEffect(() => {
    if (user) {
      setStats({
        totalSearches: user.search_count,
        searchesThisMonth: user.search_count,
        averageResults: 0 // TODO: Calculate from search history
      })
    }
  }, [user])

  if (loading) {
    return (
      <div className="min-h-screen bg-harvey-dark flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-harvey-dark flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-serif-heading text-white mb-4">Please sign in</h1>
          <Link href="/login" className="text-white underline">Sign In</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-harvey-dark py-16 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <Link href="/" className="text-gray-400 hover:text-white text-sm">
            ← Back to Search
          </Link>
        </div>

        <h1 className="text-4xl font-serif-heading text-white mb-8">Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-harvey-dark border border-gray-800 rounded-md p-6">
            <h3 className="text-sm text-gray-400 mb-2">Total Searches</h3>
            <p className="text-3xl font-bold text-white">{stats.totalSearches}</p>
          </div>
          
          <div className="bg-harvey-dark border border-gray-800 rounded-md p-6">
            <h3 className="text-sm text-gray-400 mb-2">Searches This Month</h3>
            <p className="text-3xl font-bold text-white">{stats.searchesThisMonth}</p>
          </div>
          
          <div className="bg-harvey-dark border border-gray-800 rounded-md p-6">
            <h3 className="text-sm text-gray-400 mb-2">Account Tier</h3>
            <p className="text-3xl font-bold text-white">
              {user.tier === 'pro' ? 'Pro' : 'Free'}
            </p>
            {user.tier === 'free' && (
              <Link href="/upgrade" className="text-sm text-blue-400 hover:text-blue-300 mt-2 inline-block">
                Upgrade →
              </Link>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Link
            href="/"
            className="bg-harvey-dark border border-gray-800 rounded-md p-6 hover:border-gray-700 transition-colors"
          >
            <h3 className="text-xl font-serif-heading text-white mb-2">Start New Search</h3>
            <p className="text-gray-400 text-sm">Search through legal documents and case law</p>
          </Link>
          
          <Link
            href="/profile"
            className="bg-harvey-dark border border-gray-800 rounded-md p-6 hover:border-gray-700 transition-colors"
          >
            <h3 className="text-xl font-serif-heading text-white mb-2">View Profile</h3>
            <p className="text-gray-400 text-sm">Manage your account settings and view usage</p>
          </Link>
        </div>

        {/* Usage Progress */}
        {user.tier === 'free' && (
          <div className="bg-harvey-dark border border-gray-800 rounded-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-serif-heading text-white">Free Tier Usage</h3>
              <span className="text-sm text-gray-400">
                {user.search_count} / 15 searches
              </span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-4">
              <div
                className="bg-blue-600 h-4 rounded-full transition-all"
                style={{ width: `${Math.min((user.search_count / 15) * 100, 100)}%` }}
              />
            </div>
            {user.searches_remaining <= 0 && (
              <div className="mt-4 p-4 bg-yellow-900 border border-yellow-700 rounded-md">
                <p className="text-yellow-200 text-sm mb-2">
                  You've reached your free search limit!
                </p>
                <Link
                  href="/upgrade"
                  className="text-yellow-200 hover:text-yellow-100 underline text-sm"
                >
                  Upgrade to Pro for unlimited searches →
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

