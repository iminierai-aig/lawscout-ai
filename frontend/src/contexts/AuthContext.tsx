'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User, register, login, getUser, checkSearchLimit } from '@/lib/api'
import { getToken, setToken, removeToken, setUser, getUser as getStoredUser, isAuthenticated } from '@/lib/auth'

interface AuthContextType {
  user: User | null
  token: string | null
  loading: boolean
  isAuth: boolean
  registerUser: (email: string, password: string, fullName: string) => Promise<void>
  loginUser: (email: string, password: string) => Promise<void>
  logoutUser: () => void
  refreshUser: () => Promise<void>
  checkLimit: () => Promise<{ can_search: boolean; searches_remaining: number; message: string }>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<User | null>(null)
  const [token, setTokenState] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = getToken()
      const storedUser = getStoredUser()
      
      if (storedToken && storedUser) {
        setTokenState(storedToken)
        setUserState(storedUser)
        
        // Verify token is still valid by fetching fresh user data
        try {
          const freshUser = await getUser(storedToken)
          setUserState(freshUser)
          setUser(freshUser)
        } catch (error) {
          // Token invalid, clear auth
          removeToken()
          setTokenState(null)
          setUserState(null)
        }
      }
      
      setLoading(false)
    }
    
    initAuth()
  }, [])

  const registerUser = async (email: string, password: string, fullName: string) => {
    const response = await register(email, password, fullName)
    setToken(response.access_token)
    setUser(response.user)
    setTokenState(response.access_token)
    setUserState(response.user)
    // Set cookie for middleware
    document.cookie = `lawscout_auth_token=${response.access_token}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`
  }

  const loginUser = async (email: string, password: string) => {
    const response = await login(email, password)
    setToken(response.access_token)
    setUser(response.user)
    setTokenState(response.access_token)
    setUserState(response.user)
    // Set cookie for middleware
    document.cookie = `lawscout_auth_token=${response.access_token}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`
  }

  const logoutUser = () => {
    removeToken()
    setTokenState(null)
    setUserState(null)
    // Clear cookie
    document.cookie = 'lawscout_auth_token=; path=/; max-age=0'
  }

  const refreshUser = async () => {
    const currentToken = getToken()
    if (!currentToken) {
      logoutUser()
      return
    }
    
    try {
      const freshUser = await getUser(currentToken)
      setUserState(freshUser)
      setUser(freshUser)
    } catch (error) {
      logoutUser()
    }
  }

  const checkLimit = async () => {
    const currentToken = getToken()
    if (!currentToken) {
      throw new Error('Not authenticated')
    }
    
    const limit = await checkSearchLimit(currentToken)
    return {
      can_search: limit.can_search,
      searches_remaining: limit.searches_remaining,
      message: limit.message
    }
  }

  const value: AuthContextType = {
    user,
    token,
    loading,
    isAuth: isAuthenticated(),
    registerUser,
    loginUser,
    logoutUser,
    refreshUser,
    checkLimit
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

