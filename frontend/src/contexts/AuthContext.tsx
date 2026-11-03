import { useEffect, useState, type ReactNode } from 'react'
import axios from 'axios'

import { AUTH_UNAUTHORIZED_EVENT, currentUserRequest, loginRequest, logoutRequest, setAccessToken, type AuthUser } from '../services/api'
import { authContext } from './auth-context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    function handleUnauthorized() {
      setAccessToken(null)
      setUser(null)
      setIsLoading(false)
    }

    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized)
    return () => window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized)
  }, [])

  async function login(email: string, password: string) {
    setIsLoading(true)
    setAccessToken(null)
    setUser(null)
    try {
      const token = await loginRequest(email, password)
      setAccessToken(token.access_token)
      setUser(await currentUserRequest())
    } catch (error) {
      setAccessToken(null)
      setUser(null)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  async function logout() {
    try {
      if (user) {
        await logoutRequest()
      }
    } catch (error) {
      if (!axios.isAxiosError(error) || error.response?.status !== 401) {
        throw error
      }
    } finally {
      setAccessToken(null)
      setUser(null)
    }
  }

  return <authContext.Provider value={{ user, isLoading, login, logout }}>{children}</authContext.Provider>
}
