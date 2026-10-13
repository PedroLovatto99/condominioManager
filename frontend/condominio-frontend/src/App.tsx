import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import RequireAuth from './components/RequireAuth'
import Bloco from './pages/Bloco'
import BlocosLista from './pages/BlocosLista'
import Login from './pages/Login'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/login" element={<Login />} />

        <Route element={<RequireAuth />}>
          <Route index element={<BlocosLista />} />
          <Route path="/blocos/:id" element={<Bloco />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

export default App
