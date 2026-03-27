import {
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { fetchCurrentUser, login as loginRequest, logout as logoutRequest } from '../services/auth'
import { setUnauthorizedHandler } from '../services/api'
import { getAccessToken } from '../services/storage'
import type { AuthUser, LoginPayload } from '../types/auth'
import { AuthContext, type AuthContextValue } from './auth-context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const location = useLocation()
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isBootstrapping, setIsBootstrapping] = useState(() => Boolean(getAccessToken()))

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setUser(null)
      navigate('/login', {
        replace: true,
        state: { reason: 'expired' },
      })
    })

    return () => {
      setUnauthorizedHandler(null)
    }
  }, [navigate])

  useEffect(() => {
    const token = getAccessToken()

    if (!token) {
      return
    }

    fetchCurrentUser()
      .then((currentUser) => {
        setUser(currentUser)
      })
      .catch(() => {
        logoutRequest()
        setUser(null)
      })
      .finally(() => {
        setIsBootstrapping(false)
      })
  }, [])

  async function login(payload: LoginPayload): Promise<void> {
    await loginRequest(payload)
    const currentUser = await fetchCurrentUser()
    setUser(currentUser)

    const nextPath = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname
    navigate(nextPath ?? '/', { replace: true })
  }

  function logout(): void {
    logoutRequest()
    setUser(null)
    navigate('/login', { replace: true })
  }

  const value: AuthContextValue = {
    user,
    isAuthenticated: Boolean(user),
    isBootstrapping,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
