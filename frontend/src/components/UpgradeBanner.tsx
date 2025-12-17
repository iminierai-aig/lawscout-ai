'use client'

import { useAuth } from '@/contexts/AuthContext'
import Link from 'next/link'

export default function UpgradeBanner() {
  const { user } = useAuth()

  if (!user || user.tier === 'pro') return null

  if (user.searches_remaining <= 0) {
    return (
      <div className="bg-gradient-to-r from-yellow-900 to-yellow-800 border border-yellow-700 rounded-md p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-serif-heading text-white mb-2">
              Free Search Limit Reached
            </h3>
            <p className="text-gray-300 text-sm">
              You've used all {user.search_count} free searches. Upgrade to Pro for unlimited searches!
            </p>
          </div>
          <Link
            href="/upgrade"
            className="px-6 py-3 bg-white text-harvey-dark font-medium rounded-md hover:bg-gray-100 transition-colors whitespace-nowrap"
          >
            Upgrade to Pro
          </Link>
        </div>
      </div>
    )
  }

  if (user.searches_remaining <= 3) {
    return (
      <div className="bg-blue-950 border border-blue-800 rounded-md p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-blue-200 text-sm">
              <strong>{user.searches_remaining} free searches remaining.</strong> Upgrade to Pro for unlimited access.
            </p>
          </div>
          <Link
            href="/upgrade"
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors whitespace-nowrap"
          >
            Upgrade
          </Link>
        </div>
      </div>
    )
  }

  return null
}

