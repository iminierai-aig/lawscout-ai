'use client'

import { useEffect, useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { setToken, setUser } from '@/lib/auth'

function AuthCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { refreshUser } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const token = searchParams.get('token')
    const error = searchParams.get('error')
    const provider = searchParams.get('provider')

    if (error) {
      setStatus('error')
      setMessage(error)
      setTimeout(() => router.push('/login'), 3000)
      return
    }

    if (token) {
      // Store token
      setToken(token)
      
      // Fetch user data
      const fetchUser = async () => {
        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.lawscoutai.com'
          const response = await fetch(`${apiUrl}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })

          if (response.ok) {
            const user = await response.json()
            setUser(user)
            
            // Set cookie for middleware
            document.cookie = `lawscout_auth_token=${token}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`
            
            // Refresh auth context
            await refreshUser()
            
            setStatus('success')
            setMessage(`Successfully signed in with ${provider || 'OAuth'}!`)
            setTimeout(() => router.push('/'), 1500)
          } else {
            throw new Error('Failed to fetch user data')
          }
        } catch (err) {
          setStatus('error')
          setMessage('Failed to complete authentication. Please try again.')
          setTimeout(() => router.push('/login'), 3000)
        }
      }

      fetchUser()
    } else {
      setStatus('error')
      setMessage('No token received. Please try again.')
      setTimeout(() => router.push('/login'), 3000)
    }
  }, [searchParams, router, refreshUser])

  return (
    <div className="min-h-screen bg-harvey-dark flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {status === 'loading' && (
          <>
            <div className="mb-4">
              <svg className="animate-spin h-12 w-12 text-white mx-auto" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <p className="text-white text-lg">Completing authentication...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="mb-4">
              <svg className="h-12 w-12 text-green-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-white text-lg">{message}</p>
            <p className="text-gray-400 text-sm mt-2">Redirecting...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="mb-4">
              <svg className="h-12 w-12 text-red-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <p className="text-red-400 text-lg">{message}</p>
            <p className="text-gray-400 text-sm mt-2">Redirecting to login...</p>
          </>
        )}
      </div>
    </div>
  )
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-harvey-dark flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="mb-4">
            <svg className="animate-spin h-12 w-12 text-white mx-auto" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <p className="text-white text-lg">Loading...</p>
        </div>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  )
}

