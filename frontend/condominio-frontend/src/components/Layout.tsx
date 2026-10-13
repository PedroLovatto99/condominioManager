import { FaRightFromBracket, FaUser } from 'react-icons/fa6'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import fundacao from '../assets/img/Fundacao.png'
import recanto from '../assets/img/recanto-maestro.png'
import { getEmail, limparSessao } from '../services/api'

export default function Layout() {
  const { pathname } = useLocation()
  const navigate = useNavigate()

  // Na tela de login o cabeçalho não mostra usuário nem botão de sair
  const logado = pathname !== '/login'

  function sair() {
    limparSessao()
    navigate('/login')
  }

  return (
    <>
      <header>
        <div className="header-container">
          {logado && (
            <h2>
              <FaUser /> {getEmail()}
            </h2>
          )}
          <h1>Condomínio Residencial Recanto Maestro</h1>
          {logado && (
            <div className="btn-logout">
              <button type="button" onClick={sair}>
                Sair <FaRightFromBracket />
              </button>
            </div>
          )}
        </div>
      </header>

      <main>
        <Outlet />
      </main>

      <footer>
        <div className="logoFundacao">
          <img src={fundacao} alt="Logo da Fundação" />
        </div>
        <p>2024 Copyright &copy; | Todos os direitos reservados</p>
        <div className="logoRecanto">
          <img src={recanto} alt="Logo do Recanto Maestro" />
        </div>
      </footer>
    </>
  )
}
