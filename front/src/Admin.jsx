import { useEffect, useState } from 'react'
import {
  cadastrarAdmin,
  deletarAdmin,
  listarAdministradores,
  listarConfirmacoes,
  loginAdmin,
} from './services/api'

const TOKEN_KEY = 'admin_access_token'
const USER_KEY = 'admin_user'

function Admin() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || '')
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
    } catch {
      return null
    }
  })

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  const [confirmacoes, setConfirmacoes] = useState([])
  const [admins, setAdmins] = useState([])
  const [novoAdmin, setNovoAdmin] = useState({ nome: '', username: '', password: '' })

  const isAdmin = user && (user.niveis_acesso_id === 1 || user.niveis_acesso_id === null)

  async function handleLogin(e) {
    e.preventDefault()
    setCarregando(true)
    setErro('')
    try {
      const session = await loginAdmin(username, password)
      localStorage.setItem(TOKEN_KEY, session.access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(session.user))
      setToken(session.access_token)
      setUser(session.user)
      setUsername('')
      setPassword('')
    } catch (err) {
      setErro(err.message)
    } finally {
      setCarregando(false)
    }
  }

  function handleLogout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken('')
    setUser(null)
    setConfirmacoes([])
    setAdmins([])
  }

  async function carregarDados() {
    if (!token) return
    setCarregando(true)
    setErro('')
    try {
      const conf = await listarConfirmacoes(0, 100)
      setConfirmacoes(conf.confirmados || [])
      const adm = await listarAdministradores(token, 0, 100)
      setAdmins(adm.administradores || [])
    } catch (err) {
      setErro(err.message)
      if (err.message.toLowerCase().includes('credenciais')) handleLogout()
    } finally {
      setCarregando(false)
    }
  }

  useEffect(() => {
    if (!token) return
    const run = async () => {
      await carregarDados()
    }
    run()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  async function handleCadastrarAdmin(e) {
    e.preventDefault()
    setCarregando(true)
    setErro('')
    try {
      await cadastrarAdmin(token, {
        nome: novoAdmin.nome,
        username: novoAdmin.username,
        password: novoAdmin.password,
        niveis_acesso_id: 1,
      })
      setNovoAdmin({ nome: '', username: '', password: '' })
      await carregarDados()
    } catch (err) {
      setErro(err.message)
    } finally {
      setCarregando(false)
    }
  }

  async function handleDeletarAdmin(id) {
    if (!window.confirm('Remover este administrador?')) return
    setCarregando(true)
    setErro('')
    try {
      await deletarAdmin(token, id)
      await carregarDados()
    } catch (err) {
      setErro(err.message)
    } finally {
      setCarregando(false)
    }
  }

  if (!token || !user) {
    return (
      <section id="sectionAdmin">
        <div className="admin-page">
          <div className="admin-card">
            <div className="title-form">
              <h3>Área do Administrador</h3>
              <p>Faça login para acessar o painel.</p>
            </div>
            <form className="admin-form" onSubmit={handleLogin}>
              <input
                type="text"
                placeholder="E-mail"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={carregando}
              />
              <input
                type="password"
                placeholder="Senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={carregando}
              />
              <button type="submit" disabled={carregando}>
                {carregando ? 'Entrando...' : 'Entrar'}
              </button>
              {erro && <p className="mensagem-feedback erro">{erro}</p>}
            </form>
            <a className="admin-back-link" href="/">Voltar ao site</a>
          </div>
        </div>
      </section>
    )
  }

  if (!isAdmin) {
    return (
      <section id="sectionAdmin">
        <div className="admin-page">
          <div className="admin-card">
            <p className="mensagem-feedback erro">Acesso negado. Apenas administradores.</p>
            <button className="admin-btn" onClick={handleLogout}>Sair</button>
            <a className="admin-back-link" href="/">Voltar ao site</a>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section id="sectionAdmin">
      <div className="admin-dashboard">
        <div className="admin-card">
          <div className="title-evento">
            <h3>Painel do Administrador</h3>
            <p>Olá, {user.nome}. Gerencie as confirmações e administradores.</p>
            <button className="admin-btn" onClick={handleLogout}>Sair</button>
          </div>
        </div>

        {erro && <p className="mensagem-feedback erro">{erro}</p>}

        <div className="admin-card">
          <div className="title-form">
            <h3>Confirmações de presença ({confirmacoes.length})</h3>
          </div>
          <ul className="admin-list">
            {confirmacoes.map((c) => (
              <li key={c.id}>{c.nome}</li>
            ))}
          </ul>
        </div>

        <div className="admin-card">
          <div className="title-form">
            <h3>Administradores ({admins.length})</h3>
          </div>
          <ul className="admin-list">
            {admins.map((a) => (
              <li key={a.id}>
                {a.nome} — {a.username}{' '}
                {a.id !== user.id && (
                  <button className="admin-btn admin-btn-danger" onClick={() => handleDeletarAdmin(a.id)} disabled={carregando}>
                    Remover
                  </button>
                )}
              </li>
            ))}
          </ul>

          <form className="admin-form" onSubmit={handleCadastrarAdmin}>
            <h4>Novo administrador</h4>
            <input
              type="text"
              placeholder="Nome"
              value={novoAdmin.nome}
              onChange={(e) => setNovoAdmin({ ...novoAdmin, nome: e.target.value })}
              disabled={carregando}
              required
            />
            <input
              type="text"
              placeholder="E-mail"
              value={novoAdmin.username}
              onChange={(e) => setNovoAdmin({ ...novoAdmin, username: e.target.value })}
              disabled={carregando}
              required
            />
            <input
              type="password"
              placeholder="Senha"
              value={novoAdmin.password}
              onChange={(e) => setNovoAdmin({ ...novoAdmin, password: e.target.value })}
              disabled={carregando}
              required
            />
            <button type="submit" disabled={carregando}>
              {carregando ? 'Salvando...' : 'Cadastrar'}
            </button>
          </form>
        </div>
      </div>
    </section>
  )
}

export default Admin
