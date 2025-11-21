'use client'

import { useState, useEffect } from 'react'
import ChatStream from '@/components/ChatStream'

export default function ChatPage() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking')

  useEffect(() => {
    // Verifica se backend está online
    fetch('/api/health')
      .then(async (res) => {
        const data = await res.json()
        console.log('[chat] Backend status:', data)
        if (res.ok && data.status === 'online') {
          setBackendStatus('online')
        } else {
          console.error('[chat] Backend offline:', data)
          setBackendStatus('offline')
        }
      })
      .catch((err) => {
        console.error('[chat] Erro ao verificar backend:', err)
        setBackendStatus('offline')
      })
  }, [])

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">💬 Consulta Clínica Unificada</h1>
        <p className="text-gray-600">
          Faça perguntas em português sobre dados hospitalares. O sistema combina informações 
          do banco de dados (via SQL) com documentos e protocolos (via RAG) para dar respostas completas.
        </p>
      </div>

      {backendStatus === 'offline' && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800 font-semibold">⚠️ Backend não está acessível</p>
          <p className="text-yellow-700 text-sm mt-2">
            Verifique se:
          </p>
          <ul className="text-yellow-700 text-sm mt-1 list-disc list-inside space-y-1">
            <li>A variável <code className="bg-yellow-100 px-1 rounded">NEXT_PUBLIC_API_URL</code> está configurada no Vercel</li>
            <li>O backend está rodando em: <code className="bg-yellow-100 px-1 rounded">https://assistente-dados-hospitalar.onrender.com</code></li>
            <li>O Render não está "dormindo" (configure UptimeRobot para manter ativo)</li>
          </ul>
          <p className="text-yellow-700 text-sm mt-2">
            Teste direto: <a href="https://assistente-dados-hospitalar.onrender.com/health" target="_blank" rel="noopener noreferrer" className="underline">https://assistente-dados-hospitalar.onrender.com/health</a>
          </p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <ChatStream sessionId={sessionId} />
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold mb-2">💡 Como funciona:</h3>
        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
          <li>Digite sua pergunta em português (ex: "Qual a taxa de ocupação da UTI?")</li>
          <li>O sistema busca dados no banco e documentos relevantes</li>
          <li>Você recebe resposta em tempo real com streaming</li>
          <li>SQL executado e documentos citados ficam visíveis para auditoria</li>
        </ul>
      </div>
    </div>
  )
}
