'use client'

import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface ChatStreamProps {
  sessionId: string | null
}

interface SummaryData {
  tipo: string
  ocupados?: number
  total?: number
  taxa?: number
  setor?: string
  disponiveis?: number
  label?: string
  valor?: number | string
  formato?: string
}

export default function ChatStream({ sessionId }: ChatStreamProps) {
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState('')
  const [sqlExecuted, setSqlExecuted] = useState<string | null>(null)
  const [documents, setDocuments] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(sessionId)
  const [summary, setSummary] = useState<SummaryData | null>(null)

  useEffect(() => {
    // Criar sessão ao montar componente
    const createSession = async () => {
      try {
        const sessionRes = await fetch('/api/v1/chat/sessions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 'demo-user' })
        })
        if (sessionRes.ok) {
          const sessionData = await sessionRes.json()
          setCurrentSessionId(sessionData.session_id)
        }
      } catch (error) {
        console.error('Erro ao criar sessão:', error)
      }
    }
    if (!currentSessionId) {
      createSession()
    }
  }, [currentSessionId])

  const handleSend = async () => {
    if (!message.trim()) return
    if (!currentSessionId) {
      alert('Aguardando criação de sessão...')
      return
    }
    
    setLoading(true)
    setResponse('')
    setSqlExecuted(null)
    setDocuments([])
    setSummary(null)
    
    try {
      // Usa rota de API do Next.js que faz proxy para backend
      const eventSource = new EventSource(
        `/api/v1/chat/stream?session_id=${currentSessionId}&prompt=${encodeURIComponent(message)}`
      )

      eventSource.onmessage = (e) => {
        if (e.data === '[DONE]') {
          eventSource.close()
          setLoading(false)
          return
        }

        // Oculta informações de modo interno (não relevantes para o usuário)
        if (e.data.startsWith('Modo de operação:')) {
          return
        }

        // Eventos de resumo estruturado (cards de métricas)
        if (e.data.startsWith('SUMMARY|')) {
          const payload = e.data.replace('SUMMARY|', '')
          const parts = payload.split(';').filter(Boolean)
          const obj: SummaryData = { tipo: 'generico' }
          for (const part of parts) {
            const [k, v] = part.split('=')
            if (!k) continue
            if (k === 'tipo') obj.tipo = v
            if (k === 'ocupados') obj.ocupados = Number(v)
            if (k === 'total') obj.total = Number(v)
            if (k === 'taxa') obj.taxa = Number(v)
            if (k === 'setor') obj.setor = v
            if (k === 'disponiveis') obj.disponiveis = Number(v)
            if (k === 'ocupados') {
              const numVal = Number(v)
              obj.ocupados = isNaN(numVal) ? v : numVal
            }
            if (k === 'total') {
              const numVal = Number(v)
              obj.total = isNaN(numVal) ? v : numVal
            }
            if (k === 'taxa') {
              const numVal = Number(v)
              obj.taxa = isNaN(numVal) ? v : numVal
            }
            if (k === 'label') obj.label = v
            if (k === 'valor') {
              const numVal = Number(v)
              obj.valor = isNaN(numVal) ? v : numVal
            }
            if (k === 'formato') obj.formato = v
          }
          setSummary(obj)
          // Limpa o response quando recebe summary para não mostrar dados brutos
          setResponse('')
          return
        }

        // Se já tem summary, ignora mensagens de processamento
        if (summary) {
          // Mas permite mensagens de erro/aviso
          if (e.data.includes('⚠️') || e.data.includes('❌') || e.data.includes('Erro')) {
            setResponse((prev) => (prev ? prev + '\n' + e.data : e.data))
          }
          return
        }

        // Ignora apenas mensagens de processamento técnico muito específicas
        const ignoredMessages = [
          'Analisando sua pergunta...',
          'Consultando banco de dados...',
          'Executando consulta...',
          'SQL Gerado:',
          '```sql'
        ]
        
        if (ignoredMessages.some(msg => e.data.includes(msg))) {
          return
        }

        // Ignora linhas de dados brutos (formato: "1. campo: valor, campo2: valor2")
        if (e.data.match(/^\d+\.\s+[a-z_]+:/)) {
          return
        }

        // Acumula todas as outras mensagens (incluindo erros, avisos, respostas formatadas)
        setResponse((prev) => {
          if (!prev) {
            return e.data
          }
          // Adiciona quebra de linha se necessário
          if (!prev.endsWith('\n') && !prev.endsWith('\n\n')) {
            return prev + '\n' + e.data
          }
          return prev + e.data
        })
      }

      eventSource.onerror = () => {
        eventSource.close()
        setLoading(false)
        // Se falhar, mostra mensagem amigável
        if (!response) {
          setResponse(
            '⚠️ Backend não está rodando. Para testar completamente, inicie o servidor FastAPI na porta 8000.\n\nPara iniciar:\ncd apps\\backend-fastapi\npoetry run uvicorn src.api.main:app --reload'
          )
          setSqlExecuted('-- SQL seria exibido aqui quando backend estiver rodando')
          setDocuments(['Documentos seriam citados aqui'])
        }
      }
    } catch (error) {
      setLoading(false)
      setResponse('⚠️ Erro ao conectar com o backend. Verifique se o servidor está rodando.')
    }
  }

  return (
    <div data-testid="chat-container" className="space-y-4">
      <div className="flex gap-2">
      <input
        data-testid="chat-input"
          type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
          placeholder="Ex: Qual a taxa de ocupação da UTI pediátrica?"
          className="flex-1 p-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
          disabled={loading}
      />
        <button 
          data-testid="send-button" 
          onClick={handleSend}
          disabled={loading || !message.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition font-semibold"
        >
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </div>
      
      {(response || summary) && (
        <div className="space-y-4">
          {summary && summary.tipo === 'uti_ocupacao' && (
            <div className="p-4 bg-white rounded-lg border border-blue-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <p className="text-sm text-gray-500 uppercase tracking-wide">
                  Taxa de ocupação - {summary.setor || 'UTI Pediátrica'}
                </p>
                <p className="mt-1 text-3xl font-bold text-blue-700">
                  {summary.taxa ? Number(summary.taxa).toFixed(2) : '0.00'}%
                </p>
                <p className="mt-1 text-sm text-gray-600">
                  {summary.ocupados || 0} de {summary.total || 0} leitos ocupados
                </p>
              </div>
              <div className="text-sm text-gray-500">
                <p>Faixa segura recomendada: até 80%</p>
                {summary.taxa !== undefined && summary.taxa > 80 && (
                  <p className="mt-1 text-red-600 font-semibold">
                    Alerta: ocupação acima do ideal.
                  </p>
                )}
              </div>
            </div>
          )}

          {summary && summary.tipo === 'leitos_disponiveis' && (
            <div className="p-4 bg-white rounded-lg border border-blue-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <p className="text-sm text-gray-500 uppercase tracking-wide">
                  Leitos disponíveis - {summary.setor || 'Setor consultado'}
                </p>
                <p className="mt-1 text-3xl font-bold text-blue-700">
                  {summary.disponiveis}
                </p>
                <p className="mt-1 text-sm text-gray-600">
                  Leitos marcados como &quot;disponíveis&quot; no banco de dados
                </p>
              </div>
              <div className="text-sm text-gray-500">
                <p>Baseado nos dados simulados de leitos.</p>
              </div>
            </div>
          )}

          {summary && summary.tipo === 'contagem' && (
            <div className="p-4 bg-white rounded-lg border border-blue-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <p className="text-sm text-gray-500 uppercase tracking-wide">
                  {summary.label || 'Total'}
                </p>
                <p className="mt-1 text-3xl font-bold text-blue-700">
                  {summary.valor}
                </p>
                <p className="mt-1 text-sm text-gray-600">
                  Contagem agregada com base nos dados atuais do banco.
                </p>
              </div>
              <div className="text-sm text-gray-500">
                <p>Uso típico: visão rápida de volumes (ex.: procedimentos, atendimentos).</p>
              </div>
            </div>
          )}

          {summary && summary.tipo === 'media' && (
            <div className="p-4 bg-white rounded-lg border border-blue-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <p className="text-sm text-gray-500 uppercase tracking-wide">
                  {summary.label || 'Média'}
                </p>
                <p className="mt-1 text-3xl font-bold text-blue-700">
                  {summary.formato === 'currency' 
                    ? `R$ ${Number(summary.valor).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                    : summary.valor}
                </p>
                <p className="mt-1 text-sm text-gray-600">
                  {summary.formato === 'currency' 
                    ? 'Valor médio calculado com base nos dados atuais do banco.'
                    : 'Média calculada com base nos dados atuais do banco.'}
                </p>
              </div>
              <div className="text-sm text-gray-500">
                <p>Baseado em agregação dos dados disponíveis.</p>
              </div>
            </div>
          )}

          {summary && summary.tipo === 'soma' && (
            <div className="p-4 bg-white rounded-lg border border-blue-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <p className="text-sm text-gray-500 uppercase tracking-wide">
                  {summary.label || 'Total'}
                </p>
                <p className="mt-1 text-3xl font-bold text-blue-700">
                  {summary.formato === 'currency' 
                    ? `R$ ${Number(summary.valor).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                    : summary.valor}
                </p>
                <p className="mt-1 text-sm text-gray-600">
                  {summary.formato === 'currency' 
                    ? 'Soma total calculada com base nos dados atuais do banco.'
                    : 'Total calculado com base nos dados atuais do banco.'}
                </p>
              </div>
              <div className="text-sm text-gray-500">
                <p>Baseado em agregação dos dados disponíveis.</p>
              </div>
            </div>
          )}

          {/* Quando houver card de resumo (SUMMARY), NUNCA mostra o bloco textual "Resposta" e detalhes técnicos */}
          {!summary && response && (
            <>
              <div
                data-testid="streaming-response"
                className="p-4 bg-blue-50 rounded-lg border border-blue-200"
              >
                <h3 className="font-semibold mb-2 text-blue-900">💬 Resposta:</h3>
                <div className="prose prose-sm max-w-none text-gray-800 whitespace-pre-wrap">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {response}
                  </ReactMarkdown>
                </div>
              </div>

              {sqlExecuted && (
                <div
                  data-testid="sql-executed"
                  className="p-4 bg-green-50 rounded-lg border border-green-200"
                >
                  <h3 className="font-semibold mb-2 text-green-900">
                    📊 SQL Executado:
                  </h3>
                  <pre className="bg-white p-3 rounded text-sm font-mono overflow-x-auto">
                    {sqlExecuted}
                  </pre>
                </div>
              )}

              {documents.length > 0 && (
                <div
                  data-testid="document-citations"
                  className="p-4 bg-yellow-50 rounded-lg border border-yellow-200"
                >
                  <h3 className="font-semibold mb-2 text-yellow-900">
                    📄 Documentos Citados:
                  </h3>
                  <ul className="list-disc list-inside space-y-1">
                    {documents.map((doc, idx) => (
                      <li key={idx} className="text-gray-700">
                        {doc}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {!response && !summary && !loading && (
        <div className="text-center py-8 text-gray-500">
          <p>💡 Digite sua pergunta acima para começar</p>
          <p className="text-sm mt-2">Exemplos:</p>
          <ul className="text-sm mt-2 space-y-1">
            <li>"Qual a taxa de ocupação da UTI pediátrica?"</li>
            <li>"Quantos leitos estão disponíveis no setor X?"</li>
            <li>"Qual protocolo aplicar para isolamento?"</li>
          </ul>
        </div>
      )}
    </div>
  )
}
