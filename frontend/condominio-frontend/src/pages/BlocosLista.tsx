import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import type { Bloco } from '../types'
import { corDoBloco } from '../utils/formatar'

export default function BlocosLista() {
  const [blocos, setBlocos] = useState<Bloco[] | null>(null)
  const [erro, setErro] = useState(false)

  useEffect(() => {
    let cancelado = false

    api<Bloco[]>('/blocos')
      .then((dados) => {
        if (!cancelado) setBlocos(dados)
      })
      .catch(() => {
        if (!cancelado) setErro(true)
      })

    return () => {
      cancelado = true
    }
  }, [])

  function conteudo() {
    if (erro) return <p className="mensagem erro">Não foi possível carregar os blocos.</p>
    if (!blocos) return <p className="mensagem">Carregando...</p>
    if (blocos.length === 0) return <p className="mensagem">Nenhum bloco cadastrado.</p>

    return [...blocos]
      .sort((a, b) => a.numero - b.numero)
      .map((bloco) => (
        <Link
          key={bloco.id}
          to={`/blocos/${bloco.id}`}
          style={{ backgroundColor: corDoBloco(bloco.numero) }}
        >
          <h1>Bloco {bloco.numero}</h1>
        </Link>
      ))
  }

  return (
    <>
      <h2 className="titulo-pagina">BLOCOS</h2>
      <div className="container">
        <div className="bloco">{conteudo()}</div>
      </div>
    </>
  )
}
