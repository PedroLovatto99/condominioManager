import { useState, type SubmitEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { getToken, login } from '../services/api'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  if (getToken()) {
    return <Navigate to="/" replace />
  }

  async function entrar(evento: SubmitEvent<HTMLFormElement>) {
    evento.preventDefault()
    setErro(null)
    setEnviando(true)

    try {
      await login(email.trim(), senha)
      navigate('/')
    } catch (e) {
      setErro(e instanceof Error ? e.message : 'Erro inesperado.')
      setEnviando(false)
    }
  }

  return (
    <div className="login-container">
      <h2>LOGIN</h2>
      <form className="login-form" onSubmit={entrar}>
        <div className="form-group">
          <label htmlFor="id_email">E-mail</label>
          <input
            id="id_email"
            type="email"
            autoComplete="username"
            autoFocus
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="id_senha">Senha</label>
          <input
            id="id_senha"
            type="password"
            autoComplete="current-password"
            required
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
          />
        </div>
        <button type="submit" className="login-button" disabled={enviando}>
          Entrar
        </button>
      </form>

      {erro && <p className="error-message">{erro}</p>}
    </div>
  )
}
