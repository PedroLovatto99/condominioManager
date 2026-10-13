export interface Bloco {
  id: number
  numero: number
}

export interface Apartamento {
  id: number
  bloco: Bloco
  numero: number
}

export interface Residente {
  id: number
  nome: string
  apartamento: Apartamento
  cpf: string
  telefone: number
  email: string
  data_inicio: string
  data_vencimento: string
  valor_aluguel: number
}
