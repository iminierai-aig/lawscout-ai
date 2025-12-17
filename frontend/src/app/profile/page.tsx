'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getUser } from '@/lib/api'
import { getToken } from '@/lib/auth'

export default function ProfilePage() {
  const { user, token, refreshUser, loading } = useAuth()
  const [searchHistory, setSearchHistory] = useState<any[]>([])
  const [loadingHistory, setLoadingHistory] = useState(true)

  useEffect(() => {
    if (user && token) {
      refreshUser()
      // TODO: Fetch search history from backend when endpoint is available
      setLoadingHistory(false)
    }
  }, [user, token, refreshUser])

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
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Link href="/" className="text-gray-400 hover:text-white text-sm">
            ← Back to Search
          </Link>
        </div>

        <h1 className="text-4xl font-serif-heading text-white mb-8">Profile</h1>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Account Information */}
          <div className="bg-harvey-dark border border-gray-800 rounded-md p-6">
            <h2 className="text-xl font-serif-heading text-white mb-6">Account Information</h2>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400">Email</label>
                <p className="text-white mt-1">{user.email}</p>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Full Name</label>
                <p className="text-white mt-1">{user.full_name || 'Not set'}</p>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Account Tier</label>
                <div className="mt-1">
                  {user.tier === 'pro' ? (
                    <span className="px-3 py-1 bg-yellow-600 text-white text-sm rounded-full">Pro</span>
                  ) : (
                    <span className="px-3 py-1 bg-gray-700 text-white text-sm rounded-full">Free</span>
                  )}
                </div>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Member Since</label>
                <p className="text-white mt-1">
                  {new Date(user.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
              
              {user.last_login && (
                <div>
                  <label className="text-sm text-gray-400">Last Login</label>
                  <p className="text-white mt-1">
                    {new Date(user.last_login).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Usage Statistics */}
          <div className="bg-harvey-dark border border-gray-800 rounded-md p-6">
            <h2 className="text-xl font-serif-heading text-white mb-6">Usage Statistics</h2>
            
            <div className="space-y-6">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm text-gray-400">Searches This Month</label>
                  <span className="text-2xl font-bold text-white">{user.search_count}</span>
                </div>
                {user.tier === 'free' && (
                  <div className="w-full bg-gray-800 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${Math.min((user.search_count / 15) * 100, 100)}%` }}
                    />
                  </div>
                )}
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Searches Remaining</label>
                {user.tier === 'pro' ? (
                  <p className="text-2xl font-bold text-white mt-1">Unlimited</p>
                ) : (
                  <p className="text-2xl font-bold text-white mt-1">
                    {Math.max(0, user.searches_remaining)}
                  </p>
                )}
              </div>
              
              {user.tier === 'free' && user.searches_remaining <= 3 && (
                <div className="bg-yellow-900 border border-yellow-700 rounded-md p-4">
                  <p className="text-yellow-200 text-sm mb-2">
                    Running low on searches!
                  </p>
                  <Link
                    href="/upgrade"
                    className="text-yellow-200 hover:text-yellow-100 underline text-sm"
                  >
                    Upgrade to Pro for unlimited searches →
                  </Link>
                </div>
              )}
              
              {user.tier === 'free' && (
                <Link
                  href="/upgrade"
                  className="block w-full px-4 py-3 bg-white text-harvey-dark font-medium rounded-md hover:bg-gray-100 transition-colors text-center"
                >
                  Upgrade to Pro
                </Link>
              )}
            </div>
          </div>
        </div>

        {/* Search History - Placeholder for future implementation */}
        <div className="mt-8 bg-harvey-dark border border-gray-800 rounded-md p-6">
          <h2 className="text-xl font-serif-heading text-white mb-6">Search History</h2>
          {loadingHistory ? (
            <p className="text-gray-400">Loading...</p>
          ) : searchHistory.length === 0 ? (
            <p className="text-gray-400">No search history yet. Start searching to see your queries here.</p>
          ) : (
            <div className="space-y-2">
              {searchHistory.map((search, idx) => (
                <div key={idx} className="text-gray-300 text-sm">
                  {search.query} - {new Date(search.timestamp).toLocaleDateString()}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

