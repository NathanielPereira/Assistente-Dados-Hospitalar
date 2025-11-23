'use client'

import { useState, useEffect } from 'react'

interface HealthStatus {
  status: string
  uptime_percent: number
  p95_latency_ms: number
  integrations: Record<string, { status: string; last_check: string }>
  degraded_mode: boolean
  timestamp: string
}

export default function ObservabilityPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadHealth()
    const interval = setInterval(loadHealth, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadHealth = async () => {
    try {
      const response = await fetch('/api/v1/observability/health')
      if (!response.ok) {
        throw new Error('Backend não está rodando')
      }
      const data = await response.json()
      setHealth(data)
      setError(null)
      setLoading(false)
    } catch (err: any) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto p-4 sm:p-6 max-w-6xl">
        <div className="text-center py-8 sm:py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 sm:h-12 sm:w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-sm sm:text-base text-gray-600">Carregando métricas...</p>
        </div>
      </div>
    )
  }

  if (error || !health) {
    return (
      <div className="container mx-auto p-4 sm:p-6 max-w-6xl">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 sm:p-6">
          <h2 className="text-lg sm:text-xl font-semibold text-red-800 mb-2">⚠️ Erro ao carregar métricas</h2>
          <p className="text-sm sm:text-base text-red-700">{error || 'Backend não está disponível'}</p>
          <p className="text-xs sm:text-sm text-red-600 mt-2 break-all">
            Para iniciar o backend: 
            <code className="bg-red-100 px-2 py-1 rounded ml-2 text-xs">
              cd apps\backend-fastapi && poetry run uvicorn src.api.main:app --reload
            </code>
          </p>
        </div>
      </div>
    )
  }

  const statusColor = health.status === 'healthy' ? 'text-green-600' : 'text-red-600'
  const uptimeColor = health.uptime_percent >= 99 ? 'text-green-600' : health.uptime_percent >= 95 ? 'text-yellow-600' : 'text-red-600'

  return (
    <div className="container mx-auto p-4 sm:p-6 max-w-6xl">
      <div className="mb-4 sm:mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">📊 Observability Control Room</h1>
        <p className="text-sm sm:text-base text-gray-600">
          Monitoramento em tempo real da saúde do sistema. Métricas atualizadas a cada 5 segundos.
        </p>
      </div>

      {health.degraded_mode && (
        <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-semibold text-sm sm:text-base">🚨 Modo Degradado Ativo</p>
          <p className="text-red-700 text-xs sm:text-sm mt-1">
            O sistema está operando em modo read-only devido a falhas nas integrações.
          </p>
        </div>
      )}
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-4 sm:mb-6">
        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md border-2 border-gray-200">
          <h2 className="text-xs sm:text-sm font-medium text-gray-600 mb-2">Status Geral</h2>
          <div className={`text-2xl sm:text-3xl font-bold ${statusColor} mb-1`}>
            {health.status.toUpperCase()}
          </div>
          <div className="text-xs text-gray-500">
            {health.degraded_mode ? 'Operando em modo limitado' : 'Sistema operacional'}
          </div>
        </div>
        
        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md border-2 border-gray-200">
          <h2 className="text-xs sm:text-sm font-medium text-gray-600 mb-2">Uptime</h2>
          <div className={`text-2xl sm:text-3xl font-bold ${uptimeColor} mb-1`}>
            {health.uptime_percent.toFixed(2)}%
          </div>
          <div className="text-xs text-gray-500">Meta: ≥99%</div>
        </div>
        
        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md border-2 border-gray-200 sm:col-span-2 lg:col-span-1">
          <h2 className="text-xs sm:text-sm font-medium text-gray-600 mb-2">Latência p95</h2>
          <div className="text-2xl sm:text-3xl font-bold mb-1">
            {health.p95_latency_ms.toFixed(0)}ms
          </div>
          <div className="text-xs text-gray-500">Meta: &lt;2000ms</div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">Status das Integrações</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {Object.entries(health.integrations).map(([name, info]) => (
            <div key={name} className="p-3 sm:p-4 border rounded-lg">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 mb-2">
                <h3 className="font-semibold text-sm sm:text-base">{name.toUpperCase()}</h3>
                <span className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${
                  info.status === 'ok' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {info.status === 'ok' ? '✓ OK' : '✗ FALHA'}
                </span>
              </div>
              <div className="text-xs text-gray-500">
                Última verificação: {new Date(info.last_check).toLocaleTimeString('pt-BR')}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-3 sm:p-4 text-center text-xs sm:text-sm text-gray-500">
        Última atualização: {new Date(health.timestamp).toLocaleString('pt-BR')}
      </div>
    </div>
  )
}
