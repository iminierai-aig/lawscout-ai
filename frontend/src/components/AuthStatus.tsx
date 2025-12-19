'use client'

import { useAuth } from '@/contexts/AuthContext'
import Link from 'next/link'

export default function AuthStatus() {
  const { user, isAuth, logoutUser, loading } = useAuth()

  if (loading) {
    return (
      <div className="px-4 py-2 text-sm text-gray-400">
        Loading...
      </div>
    )
  }

  if (!isAuth || !user) {
    return (
      <div className="flex items-center gap-4">
        <Link
          href="/login"
          className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors cursor-pointer"
        >
          Sign In
        </Link>
        <Link
          href="/register"
          className="px-4 py-2 text-sm bg-white text-harvey-dark rounded-md hover:bg-gray-100 transition-colors cursor-pointer"
        >
          Sign Up
        </Link>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-4">
      <div className="text-sm text-gray-400">
        <span className="text-white">{user.full_name || user.email}</span>
        {user.tier === 'pro' && (
          <span className="ml-2 px-2 py-1 bg-yellow-600 text-white text-xs rounded">Pro</span>
        )}
        {user.tier === 'free' && (
          <span className="ml-2 text-xs">
            ({user.searches_remaining} searches left)
          </span>
        )}
      </div>
      <button
        onClick={logoutUser}
        className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
      >
        Sign Out
      </button>
    </div>
  )
}

