const API_URL = import.meta.env.PROD ? '' : (import.meta.env.VITE_API_URL || 'http://localhost:8000')

function authHeaders(token) {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  return headers
}

export async function confirmarPresenca(nome) {
  const response = await fetch(`${API_URL}/api/v1/confirmacoes/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome }),
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || 'Erro ao confirmar presença.')
  }

  return data
}

export async function listarConfirmacoes(offset = 0, limit = 10) {
  const params = new URLSearchParams({ offset, limit })
  const response = await fetch(`${API_URL}/api/v1/confirmacoes/?${params}`)

  if (!response.ok) {
    throw new Error('Erro ao buscar confirmações.')
  }

  return response.json()
}

export async function loginAdmin(username, password) {
  const body = new URLSearchParams()
  body.append('username', username)
  body.append('password', password)

  const response = await fetch(`${API_URL}/api/v1/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || 'Usuário ou senha inválidos.')
  }

  return data
}

export async function listarAdministradores(token, offset = 0, limit = 10) {
  const params = new URLSearchParams({ offset, limit })
  const response = await fetch(`${API_URL}/api/v1/admin/?${params}`, {
    headers: authHeaders(token),
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || 'Erro ao buscar administradores.')
  }

  return data
}

export async function cadastrarAdmin(token, admin) {
  const response = await fetch(`${API_URL}/api/v1/admin/`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify(admin),
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || 'Erro ao cadastrar administrador.')
  }

  return data
}

export async function deletarAdmin(token, adminId) {
  const response = await fetch(`${API_URL}/api/v1/admin/${adminId}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || 'Erro ao remover administrador.')
  }

  return data
}
