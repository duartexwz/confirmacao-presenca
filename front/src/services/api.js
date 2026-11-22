/**
 * Serviço de comunicação com a API de confirmação de presença.
 *
 * Centraliza todas as chamadas HTTP ao backend FastAPI.
 * A URL base da API é definida pela variável de ambiente VITE_API_URL
 * (padrão: http://localhost:8000 em desenvolvimento).
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Registra a confirmação de presença de um convidado.
 *
 * @param {string} nome - Nome completo do convidado.
 * @returns {Promise<{id: string, nome: string}>} Dados da confirmação criada.
 * @throws {Error} Se o convidado já confirmou (409) ou erro de rede.
 */
export async function confirmarPresenca(nome) {
  const response = await fetch(`${API_URL}/confirmacoes/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || 'Erro ao confirmar presença.')
  }

  return data
}

/**
 * Lista as confirmações de presença com paginação.
 *
 * @param {number} [offset=0] - Registros a pular.
 * @param {number} [limit=10] - Registros por página.
 * @returns {Promise<{total: number, confirmados: Array}>} Lista paginada.
 */
export async function listarConfirmacoes(offset = 0, limit = 10) {
  const params = new URLSearchParams({ offset, limit })
  const response = await fetch(`${API_URL}/confirmacoes/?${params}`)

  if (!response.ok) {
    throw new Error('Erro ao buscar confirmações.')
  }

  return response.json()
}
