// Mesmas cores que o sistema antigo (Django) oferecia para os blocos.
// A API ainda não tem o campo "cor", então ela é escolhida pelo número do bloco.
const CORES_BLOCO = ['#FFD700', '#1F497D', '#00B050']

export function corDoBloco(numero: number): string {
  return CORES_BLOCO[(numero - 1) % CORES_BLOCO.length]
}

// "2026-01-31" -> "31/01/2026" (sem passar por Date, para não sofrer com fuso horário)
export function formatarData(iso: string): string {
  const [ano, mes, dia] = iso.split('-')
  return `${dia}/${mes}/${ano}`
}

export function formatarDinheiro(valor: number): string {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function formatarTelefone(telefone: number): string {
  const digitos = String(telefone)
  if (digitos.length === 11) {
    return `(${digitos.slice(0, 2)}) ${digitos.slice(2, 7)}-${digitos.slice(7)}`
  }
  if (digitos.length === 10) {
    return `(${digitos.slice(0, 2)}) ${digitos.slice(2, 6)}-${digitos.slice(6)}`
  }
  return digitos
}
