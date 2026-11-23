import { useEffect, useState } from 'react'
import './Admin.css'
import {
  cadastrarAdmin,
  deletarAdmin,
  listarAdministradores,
  listarConfirmacoes,
  loginAdmin,
  removerConfirmacao,
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
  const [modalOpen, setModalOpen] = useState(false)
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
      if (String(err.message).toLowerCase().includes('credenciais')) handleLogout()
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
      setModalOpen(false)
      await carregarDados()
    } catch (err) {
      setErro(err.message)
    } finally {
      setCarregando(false)
    }
  }

  async function handleRemoverConfirmacao(id) {
    if (!window.confirm('Remover esta confirmação?')) return
    setCarregando(true)
    setErro('')
    try {
      await removerConfirmacao(token, id)
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
        <div className="admin-login-page">
          <div className="admin-login-card">
            <div className="admin-login-header">
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
                required
              />
              <input
                type="password"
                placeholder="Senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={carregando}
                required
              />
              <button className="admin-btn admin-btn-primary" type="submit" disabled={carregando}>
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
        <div className="admin-login-page">
          <div className="admin-login-card">
            <p className="mensagem-feedback erro">Acesso negado. Apenas administradores.</p>
            <button className="admin-btn admin-btn-danger" onClick={handleLogout}>Sair</button>
            <a className="admin-back-link" href="/">Voltar ao site</a>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section id="sectionAdmin">
      <aside className="admin-sidebar">
        <div className="admin-sidebar-brand">
          <h2>Admin</h2>
          <span>Confirmação de Presença</span>
        </div>
        <div className="admin-sidebar-user">
          <span className="admin-sidebar-user-name">{user.nome}</span>
          <span className="admin-sidebar-user-email">{user.username}</span>
        </div>
        <nav className="admin-sidebar-nav">
          <span className="admin-sidebar-link active">Dashboard</span>
        </nav>
        <div className="admin-sidebar-footer">
          <button className="admin-btn admin-btn-danger" onClick={handleLogout}>
            Sair
          </button>
        </div>
      </aside>

      <main className="admin-main">
        {erro && <p className="mensagem-feedback erro admin-alert">{erro}</p>}

        <div className="admin-grid">
        <div className="admin-panel">
          <div className="admin-panel-header">
            <h3>Confirmações de presença</h3>
            <span className="admin-badge">{confirmacoes.length}</span>
          </div>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Nome</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {confirmacoes.length === 0 && (
                  <tr>
                    <td colSpan="3" className="admin-empty">Nenhuma confirmação.</td>
                  </tr>
                )}
                {confirmacoes.map((c, idx) => (
                  <tr key={c.id}>
                    <td>{idx + 1}</td>
                    <td>{c.nome}</td>
                    <td>
                      <button
                        className="admin-btn admin-btn-danger admin-btn-sm"
                        onClick={() => handleRemoverConfirmacao(c.id)}
                        disabled={carregando}
                      >
                        Remover
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="admin-panel">
          <div className="admin-panel-header">
            <h3>Administradores</h3>
            <div className="admin-panel-actions">
              <span className="admin-badge">{admins.length}</span>
              <button
                className="admin-btn admin-btn-primary admin-btn-sm"
                onClick={() => setModalOpen(true)}
                disabled={carregando}
              >
                Novo admin
              </button>
            </div>
          </div>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>E-mail</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {admins.length === 0 && (
                  <tr>
                    <td colSpan="3" className="admin-empty">Nenhum administrador.</td>
                  </tr>
                )}
                {admins.map((a) => (
                  <tr key={a.id}>
                    <td>{a.nome}</td>
                    <td>{a.username}</td>
                    <td>
                      {a.id !== user.id ? (
                        <button
                          className="admin-btn admin-btn-danger admin-btn-sm"
                          onClick={() => handleDeletarAdmin(a.id)}
                          disabled={carregando}
                        >
                          Remover
                        </button>
                      ) : (
                        <span className="admin-you">você</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      </main>

      {modalOpen && (
        <div className="admin-modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h3>Cadastrar administrador</h3>
              <button className="admin-modal-close" onClick={() => setModalOpen(false)}>×</button>
            </div>
            <form className="admin-form" onSubmit={handleCadastrarAdmin}>
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
              <div className="admin-modal-actions">
                <button
                  type="button"
                  className="admin-btn admin-btn-ghost"
                  onClick={() => setModalOpen(false)}
                  disabled={carregando}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="admin-btn admin-btn-primary"
                  disabled={carregando}
                >
                  {carregando ? 'Salvando...' : 'Cadastrar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  )
}

export default Admin
