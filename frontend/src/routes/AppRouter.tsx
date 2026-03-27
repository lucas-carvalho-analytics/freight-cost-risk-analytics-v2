import { Navigate, Route, Routes } from 'react-router-dom'
import { LoginPage } from '../pages/LoginPage'
import { DashboardPage } from '../pages/DashboardPage'
import { ProtectedRoute } from '../components/ProtectedRoute'

export function AppRouter() {
  return (
    <Routes>
      <Route element={<LoginPage />} path="/login" />
      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardPage />} path="/" />
      </Route>
      <Route element={<Navigate replace to="/" />} path="*" />
    </Routes>
  )
}
