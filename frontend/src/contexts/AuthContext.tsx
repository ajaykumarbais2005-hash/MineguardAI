import { useEffect, useState, type ReactNode } from 'react'
import axios from 'axios'

import { AUTH_TOKEN_KEY, currentUserRequest, loginRequest, logoutRequest, type AuthUser } from '../services/api'
import { authContext } from './auth-context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(() => Boolean(localStorage.getItem(AUTH_TOKEN_KEY)))

  useEffect(() => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY)
    if (!token) {
      return
    }

    currentUserRequest()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(AUTH_TOKEN_KEY)
        setUser(null)
        
      })
      .finally(() => setIsLoading(false))
  }, [])

  async function login(email: string, password: string) {
    const token = await loginRequest(email, password)
    localStorage.setItem(AUTH_TOKEN_KEY, token.access_token)
    setUser(await currentUserRequest())
  }

  async function logout() {
    try {
      if (localStorage.getItem(AUTH_TOKEN_KEY)) {
        await logoutRequest()
      }
    } catch (error) {
      if (!axios.isAxiosError(error) || error.response?.status !== 401) {
        throw error
      }
    } finally {
      localStorage.removeItem(AUTH_TOKEN_KEY)
      setUser(null)
    }
  }

  return <authContext.Provider value={{ user, isLoading, login, logout }}>{children}</authContext.Provider>
}
