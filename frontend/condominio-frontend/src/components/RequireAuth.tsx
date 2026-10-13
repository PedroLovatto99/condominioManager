import { Navigate, Outlet } from 'react-router-dom'
import { getToken } from '../services/api'

export default function RequireAuth() {
  return getToken() ? <Outlet /> : <Navigate to="/login" replace />
}
