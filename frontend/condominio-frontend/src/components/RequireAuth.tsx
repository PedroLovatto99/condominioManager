import { Navigate, Outlet } from 'react-router-dom'
import { getToken } from '../services/api'

// Rotas filhas só abrem com token; sem ele, volta para o login.
export default function RequireAuth() {
  return getToken() ? <Outlet /> : <Navigate to="/login" replace />
}
