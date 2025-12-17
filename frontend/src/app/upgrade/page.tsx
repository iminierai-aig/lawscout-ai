'use client'

import { useAuth } from '@/contexts/AuthContext'
import Link from 'next/link'

export default function UpgradePage() {
  const { user } = useAuth()

  if (!user) {
    return (
      <div className="min-h-screen bg-harvey-dark flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-serif-heading text-white mb-4">Please sign in to upgrade</h1>
          <Link href="/login" className="text-white underline">Sign In</Link>
        </div>
      </div>
    )
  }

  if (user.tier === 'pro') {
    return (
      <div className="min-h-screen bg-harvey-dark flex items-center justify-center px-4">
        <div className="max-w-2xl w-full text-center">
          <h1 className="text-4xl font-serif-heading text-white mb-4">You're already on Pro!</h1>
          <p className="text-gray-400 mb-8">Enjoy unlimited searches.</p>
          <Link href="/" className="text-white underline">Back to Search</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-harvey-dark py-16 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-serif-heading text-white mb-4">Upgrade to Pro</h1>
          <p className="text-gray-400 text-lg">Unlock unlimited legal research</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Free Tier */}
          <div className="bg-harvey-dark border border-gray-800 rounded-md p-8">
            <h2 className="text-2xl font-serif-heading text-white mb-4">Free</h2>
            <div className="text-4xl font-bold text-white mb-6">$0<span className="text-lg text-gray-400">/month</span></div>
            <ul className="space-y-3 mb-8">
              <li className="text-gray-400">✓ 15 searches per month</li>
              <li className="text-gray-400">✓ Basic search features</li>
              <li className="text-gray-400">✓ Case law & contracts</li>
            </ul>
            <div className="px-4 py-2 bg-gray-800 text-gray-400 rounded-md text-center">
              Current Plan
            </div>
          </div>

          {/* Pro Tier */}
          <div className="bg-gradient-to-br from-yellow-900 to-yellow-800 border-2 border-yellow-600 rounded-md p-8 relative">
            <div className="absolute top-4 right-4 px-3 py-1 bg-yellow-600 text-white text-xs rounded-full">
              RECOMMENDED
            </div>
            <h2 className="text-2xl font-serif-heading text-white mb-4">Pro</h2>
            <div className="text-4xl font-bold text-white mb-6">$49<span className="text-lg text-gray-300">/month</span></div>
            <ul className="space-y-3 mb-8">
              <li className="text-white">✓ Unlimited searches</li>
              <li className="text-white">✓ All search features</li>
              <li className="text-white">✓ Priority support</li>
              <li className="text-white">✓ Advanced filters</li>
              <li className="text-white">✓ Export capabilities</li>
            </ul>
            <button className="w-full px-6 py-3 bg-white text-harvey-dark font-medium rounded-md hover:bg-gray-100 transition-colors">
              Contact to Upgrade
            </button>
            <p className="text-xs text-gray-300 mt-4">
              Contact admin to upgrade your account
            </p>
          </div>
        </div>

        <div className="text-center">
          <Link href="/" className="text-gray-400 hover:text-white">
            ← Back to Search
          </Link>
        </div>
      </div>
    </div>
  )
}

