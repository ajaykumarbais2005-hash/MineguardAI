import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '../contexts/useAuth'

export default function ProtectedRoute() {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return <div className="auth-loading">Checking secure session...</div>
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}
