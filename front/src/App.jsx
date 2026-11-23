import { useState } from 'react'
import './App.css'
import { confirmarPresenca } from './services/api'
import Admin from './Admin'

/**
 * Componente principal da aplicação.
 *
 * Exibe as informações do evento e o formulário de confirmação de presença.
 * Ao submeter o formulário, envia o nome do convidado para a API
 * e exibe feedback visual de sucesso ou erro.
 */
function App() {
  const [view, setView] = useState('home')
  const [nome, setNome] = useState('')
  const [mensagem, setMensagem] = useState('')
  const [tipoMensagem, setTipoMensagem] = useState('')   // 'sucesso' | 'erro'
  const [carregando, setCarregando] = useState(false)

  /**
   * Envia a confirmação de presença para a API.
   * Exibe mensagem de sucesso ou erro conforme a resposta.
   */
  async function handleSubmit(e) {
    e.preventDefault()

    const nomeTrimmed = nome.trim()
    if (!nomeTrimmed) {
      setMensagem('Por favor, digite seu nome completo.')
      setTipoMensagem('erro')
      return
    }

    setCarregando(true)
    setMensagem('')

    try {
      await confirmarPresenca(nomeTrimmed)
      setMensagem(`Presença de "${nomeTrimmed}" confirmada com sucesso! ✨`)
      setTipoMensagem('sucesso')
      setNome('')
    } catch (error) {
      setMensagem(error.message)
      setTipoMensagem('erro')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <>
     <nav style={{ padding: '1rem', textAlign: 'right' }}>
       <button onClick={() => setView(view === 'home' ? 'admin' : 'home')}>
         {view === 'home' ? 'Área do Admin' : 'Voltar'}
       </button>
     </nav>
     {view === 'admin' ? <Admin /> : (
     <section id='sectionConfirmation'>
        <div className='container-section'>
          <div className='container-informacoes'>
            <div className='title-evento'>
              <h3>Jantar de Noivado - Mayckon e Duda</h3>
              <p>Demos mais um passo importante em nossa jornada e queremos compartilhar a alegria do nosso JANTAR DE NOIVADO &amp; CHÁ DE PANELA com as pessoas que fazem parte da nossa história!</p>
            </div>
            <div className='informacoes-principais'>
              <h4>28 | Novembro | 2026</h4>
              <p className='horario'>às 19h00</p>
              <p className='endereco'>Colônia agrícola IAPI, Chácara 23b, lote 5</p>
              <p className='paragrafo-presenca'>Contamos com a sua presença para tornar essa noite ainda mais especial e inesquecível!</p>
              <p className='atenciosamente'>Com carinho,</p>
              <h2>Mayckon &amp; Duda</h2>
            </div>
          </div>
          <div className='container-confirmacao'>
            <div className='title-form'>
              <h3>Confirme sua presença com seu nome completo abaixo</h3>
              <p>Caso tenha algum acompanhante ou dependente que tenha sido convidado junto com você, basta digitar o nome e confirmar a presença também!</p>
            </div>
            <form id='formConfirmacao' onSubmit={handleSubmit}>
              <input
                type='text'
                name='nomeConvidado'
                id='nomeConvidado'
                placeholder='Ex: José dos Campos Ribeiro'
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                disabled={carregando}
              />
              <button
                id='enviarConfirmacao'
                type='submit'
                disabled={carregando}
              >
                {carregando ? 'Confirmando...' : 'Confirmar minha presença'}
              </button>

              {mensagem && (
                <p className={`mensagem-feedback ${tipoMensagem}`}>
                  {mensagem}
                </p>
              )}
            </form>
          </div>
        </div>
     </section>
     )}
    </>
  )
}

export default App
