import { createContext } from 'react'

import type { AuthUser } from '../services/api'

export type AuthContextValue = {
  user: AuthUser | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

export const authContext = createContext<AuthContextValue | undefined>(undefined)
