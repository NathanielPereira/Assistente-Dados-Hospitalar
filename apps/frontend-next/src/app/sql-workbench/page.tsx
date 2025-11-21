'use client'

import { useState } from 'react'
import ResultInsights from '@/components/ResultInsights'

export default function SQLWorkbenchPage() {
  const [prompt, setPrompt] = useState('')
  const [suggestedSQL, setSuggestedSQL] = useState('')
  const [approvedSQL, setApprovedSQL] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [insights, setInsights] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSuggest = async () => {
    if (!prompt.trim()) return
    
    setLoading(true)
    setError(null)
    try {
    const response = await fetch('/api/v1/sql/assist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, tables: [] }),
      })
      
      if (!response.ok) {
        throw new Error('Backend não está rodando')
      }
      
      const data = await response.json()
      setSuggestedSQL(data.sql)
      setApprovedSQL(data.sql)
    } catch (err: any) {
      setError(err.message || 'Erro ao sugerir SQL')
    } finally {
      setLoading(false)
    }
  }

  const handleExecute = async () => {
    if (!approvedSQL.trim()) return
    
    setLoading(true)
    setError(null)
    try {
    const response = await fetch('/api/v1/sql/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sql: approvedSQL, approved: true }),
      })
      
      if (!response.ok) {
        throw new Error('Erro ao executar SQL')
      }
      
      const data = await response.json()
      setResults(data.results || [])
      setInsights({ 
        summary: `Consulta retornou ${data.row_count || data.results?.length || 0} registro(s)`,
        insights: data.summary || 'Resultados carregados com sucesso'
      })
    } catch (err: any) {
      setError(err.message || 'Erro ao executar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">🔧 SQL Workbench</h1>
        <p className="text-gray-600">
          Descreva o que você quer consultar em português e receba sugestões de SQL. 
          Edite, revise e execute com segurança - tudo rastreado para auditoria.
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">⚠️ {error}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">1. Descreva sua consulta</h2>
        <div className="flex gap-2">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ex: calcular receita média por especialidade"
            className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            onKeyPress={(e) => e.key === 'Enter' && handleSuggest()}
        />
          <button
            onClick={handleSuggest}
            disabled={loading || !prompt.trim()}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            {loading ? '...' : '✨ Sugerir SQL'}
        </button>
        </div>
      </div>

      {suggestedSQL && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">2. Revise e edite o SQL sugerido</h2>
          <textarea
            value={approvedSQL}
            onChange={(e) => setApprovedSQL(e.target.value)}
            className="w-full h-40 p-4 border rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500"
            placeholder="SQL aparecerá aqui..."
          />
          <div className="mt-4 flex gap-2">
          <button
            onClick={handleExecute}
              disabled={loading || !approvedSQL.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
              {loading ? 'Executando...' : '▶️ Executar SQL Aprovado'}
            </button>
            <button
              onClick={() => {
                setSuggestedSQL('')
                setApprovedSQL('')
                setResults([])
                setInsights(null)
              }}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              Limpar
          </button>
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">3. Resultados</h2>
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">
              {results.length} registro(s) retornado(s)
            </p>
            <div className="overflow-x-auto max-h-96 border rounded-lg">
              <pre className="p-4 bg-gray-50 text-sm overflow-auto">
                {JSON.stringify(results.slice(0, 10), null, 2)}
                {results.length > 10 && `\n... e mais ${results.length - 10} registros`}
          </pre>
            </div>
          </div>
          {insights && <ResultInsights {...insights} />}
        </div>
      )}

      <div className="mt-6 p-4 bg-green-50 rounded-lg">
        <h3 className="font-semibold mb-2">🔒 Segurança:</h3>
        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
          <li>SQL nunca é executado automaticamente - você precisa aprovar</li>
          <li>Todas as execuções são registradas para auditoria</li>
          <li>Dados sensíveis são mascarados automaticamente</li>
        </ul>
      </div>
    </div>
  )
}
