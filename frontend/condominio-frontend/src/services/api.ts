const TOKEN_KEY = 'token'
const EMAIL_KEY = 'email'

// O Vite (em desenvolvimento) repassa /api/... para a FastAPI, então não precisa de CORS.
const API = '/api'

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function getEmail(): string {
  try {
    return localStorage.getItem(EMAIL_KEY) ?? ''
  } catch {
    return ''
  }
}

export function limparSessao() {
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(EMAIL_KEY)
  } catch {
    // sem localStorage (modo privado, por exemplo): não há o que limpar
  }
}

function salvarSessao(token: string, email: string) {
  try {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(EMAIL_KEY, email)
  } catch {
    // sem localStorage: o login funciona, mas não persiste
  }
}

export async function login(email: string, senha: string) {
  let resposta: Response
  try {
    resposta = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, senha }),
    })
  } catch {
    throw new Error('Não foi possível conectar ao servidor.')
  }

  if (resposta.status === 400 || resposta.status === 422) {
    throw new Error('Erro ao tentar fazer login. Verifique suas credenciais e tente novamente.')
  }
  if (!resposta.ok) {
    throw new Error('O servidor não respondeu como esperado. Tente novamente em instantes.')
  }

  const dados = await resposta.json()
  salvarSessao(dados.acess_token, email)
}

export async function api<T>(caminho: string): Promise<T> {
  const resposta = await fetch(`${API}${caminho}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })

  if (resposta.status === 401) {
    limparSessao()
    window.location.assign('/login')
    throw new Error('Sessão expirada')
  }
  if (!resposta.ok) {
    throw new Error(`Erro ${resposta.status} ao buscar ${caminho}`)
  }
  return resposta.json()
}
