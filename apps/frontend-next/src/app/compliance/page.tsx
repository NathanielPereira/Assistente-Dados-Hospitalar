'use client'

import { useState, useEffect } from 'react'

interface AuditEntry {
  session_id: string
  user_id: string
  prompt: string
  sql_executed: string | null
  timestamp: string
  legal_basis: string
}

export default function CompliancePage() {
  const [entries, setEntries] = useState<AuditEntry[]>([])
  const [filterUser, setFilterUser] = useState('')
  const [filterDays, setFilterDays] = useState(7)
  const [format, setFormat] = useState<'csv' | 'json'>('json')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAuditEntries()
  }, [filterUser, filterDays])

  const loadAuditEntries = async () => {
    setLoading(true)
    setError(null)
    try {
    const params = new URLSearchParams({
      days: filterDays.toString(),
      format: 'json',
      })
      if (filterUser) params.append('user_id', filterUser)
    
      const response = await fetch(`/api/v1/audit/exports?${params}`)
      if (!response.ok) {
        throw new Error('Backend não está rodando. Inicie o servidor FastAPI na porta 8000.')
      }
      const data = await response.json()
      setEntries(data.audit_entries || [])
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar dados de auditoria')
      setEntries([])
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
    const params = new URLSearchParams({
      days: filterDays.toString(),
      format,
      })
      if (filterUser) params.append('user_id', filterUser)
    
      const response = await fetch(`/api/v1/audit/exports?${params}`)
      if (!response.ok) {
        throw new Error('Erro ao exportar')
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `audit-export.${format}`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      alert('Erro ao exportar. Verifique se o backend está rodando.')
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">📋 Painel de Conformidade</h1>
        <p className="text-gray-600">
          Visualize e exporte trilhas de auditoria para compliance LGPD/HIPAA. 
          Todas as interações são registradas com hashes imutáveis.
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-semibold">⚠️ {error}</p>
          <p className="text-red-600 text-sm mt-1">
            Para iniciar o backend: <code className="bg-red-100 px-2 py-1 rounded">cd apps\backend-fastapi && poetry run uvicorn src.api.main:app --reload</code>
          </p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Filtros e Exportação</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Usuário</label>
        <input
          type="text"
              placeholder="Filtrar por ID de usuário"
          value={filterUser}
          onChange={(e) => setFilterUser(e.target.value)}
              className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Período</label>
        <select
          value={filterDays}
          onChange={(e) => setFilterDays(Number(e.target.value))}
              className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
        >
          <option value={7}>Últimos 7 dias</option>
          <option value={30}>Últimos 30 dias</option>
          <option value={90}>Últimos 90 dias</option>
        </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Formato</label>
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value as 'csv' | 'json')}
              className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
        >
          <option value="csv">CSV</option>
          <option value="json">JSON</option>
        </select>
          </div>
          <div className="flex items-end">
        <button
          onClick={handleExport}
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
              {loading ? 'Carregando...' : '📥 Exportar'}
        </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="text-xl font-semibold">Registros de Auditoria</h2>
          <p className="text-sm text-gray-600 mt-1">
            {entries.length} registro(s) encontrado(s)
          </p>
        </div>
        
        {loading ? (
          <div className="p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Carregando...</p>
          </div>
        ) : entries.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>Nenhum registro encontrado para os filtros selecionados.</p>
            {!error && <p className="text-sm mt-2">Tente ajustar os filtros ou verifique se há dados no sistema.</p>}
          </div>
        ) : (
      <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Session ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Usuário</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Pergunta</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">SQL</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Base Legal</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Data/Hora</th>
            </tr>
          </thead>
              <tbody className="bg-white divide-y divide-gray-200">
            {entries.map((entry, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 transition">
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">
                      {entry.session_id.substring(0, 12)}...
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{entry.user_id}</td>
                    <td className="px-4 py-3 text-sm text-gray-700 max-w-xs truncate" title={entry.prompt}>
                      {entry.prompt.substring(0, 60)}...
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {entry.sql_executed ? (
                        <code className="bg-gray-100 px-2 py-1 rounded text-xs font-mono">
                          {entry.sql_executed.substring(0, 40)}...
                        </code>
                      ) : (
                        <span className="text-gray-400">N/A</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{entry.legal_basis}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(entry.timestamp).toLocaleString('pt-BR')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
          </div>
        )}
      </div>
    </div>
  )
}
