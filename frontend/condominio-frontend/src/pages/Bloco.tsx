import { useEffect, useState } from 'react'
import { FaLeftLong } from 'react-icons/fa6'
import { Link, useParams } from 'react-router-dom'
import { api } from '../services/api'
import type { Apartamento, Bloco, Residente } from '../types'
import {
  corDoBloco,
  formatarData,
  formatarDinheiro,
  formatarTelefone,
} from '../utils/formatar'

interface Dados {
  bloco: Bloco
  apartamentos: Apartamento[]
  residentes: Residente[]
}

const COLUNAS: { titulo: string; valor: (residente: Residente) => string }[] = [
  { titulo: 'RESIDENTE(S)', valor: (r) => r.nome },
  { titulo: 'CPF', valor: (r) => r.cpf },
  { titulo: 'TELEFONE', valor: (r) => formatarTelefone(r.telefone) },
  { titulo: 'E-MAIL', valor: (r) => r.email },
  { titulo: 'DATA DE INÍCIO', valor: (r) => formatarData(r.data_inicio) },
  { titulo: 'DATA DE VENCIMENTO', valor: (r) => formatarData(r.data_vencimento) },
  { titulo: 'VALOR DO ALUGUEL', valor: (r) => formatarDinheiro(r.valor_aluguel) },
]

export default function BlocoPagina() {
  const blocoId = Number(useParams().id)
  const [dados, setDados] = useState<Dados | null>(null)
  const [erroId, setErroId] = useState<number | null>(null)

  useEffect(() => {
    let cancelado = false

    Promise.all([
      api<Bloco>(`/blocos/${blocoId}`),
      api<Apartamento[]>('/apartamentos'),
      api<Residente[]>('/residentes'),
    ])
      .then(([bloco, apartamentos, residentes]) => {
        if (!cancelado) setDados({ bloco, apartamentos, residentes })
      })
      .catch(() => {
        if (!cancelado) setErroId(blocoId)
      })

    return () => {
      cancelado = true
    }
  }, [blocoId])

  const atual = dados?.bloco.id === blocoId ? dados : null
  const bloco = atual?.bloco

  useEffect(() => {
    if (!bloco) return
    document.body.style.backgroundColor = corDoBloco(bloco.numero)
    return () => {
      document.body.style.backgroundColor = ''
    }
  }, [bloco])

  const apartamentos = (atual?.apartamentos ?? [])
    .filter((apartamento) => apartamento.bloco.id === blocoId)
    .sort((a, b) => a.numero - b.numero)

  function aviso() {
    if (erroId === blocoId) return <p className="mensagem erro">Não foi possível carregar o bloco.</p>
    if (!atual) return <p className="mensagem">Carregando...</p>
    if (apartamentos.length === 0) {
      return <p className="mensagem">Nenhum apartamento cadastrado neste bloco.</p>
    }
    return null
  }

  return (
    <div className="container">
      <div className="header">
        <h1 className="sticky-header">{bloco ? `BLOCO ${bloco.numero}` : 'BLOCO'}</h1>
      </div>

      <div className="action-buttons">
        <div className="back-button sticky-buttons">
          <Link to="/">
            <FaLeftLong /> Voltar para a lista de blocos
          </Link>
        </div>
      </div>

      {aviso()}

      <div className="apartamentos-residentes-container">
        <table className="apartamentos-residentes">
          <thead>
            <tr>
              <th>APARTAMENTO</th>
              {COLUNAS.map((coluna) => (
                <th key={coluna.titulo}>{coluna.titulo}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {apartamentos.map((apartamento) => {
              const moradores = (atual?.residentes ?? []).filter(
                (residente) => residente.apartamento.id === apartamento.id,
              )
              return (
                <tr key={apartamento.id}>
                  <td className="numero-apartamento">{apartamento.numero}</td>
                  {COLUNAS.map((coluna) => (
                    <td key={coluna.titulo}>
                      {moradores.map((residente) => (
                        <div className="residente-info" key={residente.id}>
                          <span>{coluna.valor(residente)}</span>
                        </div>
                      ))}
                    </td>
                  ))}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
