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
      <div className="container mx-auto p-6 max-w-6xl">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Carregando métricas...</p>
        </div>
      </div>
    )
  }

  if (error || !health) {
    return (
      <div className="container mx-auto p-6 max-w-6xl">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-red-800 mb-2">⚠️ Erro ao carregar métricas</h2>
          <p className="text-red-700">{error || 'Backend não está disponível'}</p>
          <p className="text-red-600 text-sm mt-2">
            Para iniciar o backend: 
            <code className="bg-red-100 px-2 py-1 rounded ml-2">
              cd apps\backend-fastapi && poetry run uvicorn src.api.main:app --reload
            </code>
          </p>
        </div>
      </div>
    )
  }

  const statusColor = health.status === 'healthy' ? 'green' : 'red'
  const uptimeColor = health.uptime_percent >= 99 ? 'green' : health.uptime_percent >= 95 ? 'yellow' : 'red'

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">📊 Observability Control Room</h1>
        <p className="text-gray-600">
          Monitoramento em tempo real da saúde do sistema. Métricas atualizadas a cada 5 segundos.
        </p>
      </div>

      {health.degraded_mode && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-semibold">🚨 Modo Degradado Ativo</p>
          <p className="text-red-700 text-sm mt-1">
            O sistema está operando em modo read-only devido a falhas nas integrações.
          </p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md border-2 border-gray-200">
          <h2 className="text-sm font-medium text-gray-600 mb-2">Status Geral</h2>
          <div className={`text-3xl font-bold text-${statusColor}-600 mb-1`}>
            {health.status.toUpperCase()}
          </div>
          <div className="text-xs text-gray-500">
            {health.degraded_mode ? 'Operando em modo limitado' : 'Sistema operacional'}
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border-2 border-gray-200">
          <h2 className="text-sm font-medium text-gray-600 mb-2">Uptime</h2>
          <div className={`text-3xl font-bold text-${uptimeColor}-600 mb-1`}>
            {health.uptime_percent.toFixed(2)}%
          </div>
          <div className="text-xs text-gray-500">Meta: ≥99%</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border-2 border-gray-200">
          <h2 className="text-sm font-medium text-gray-600 mb-2">Latência p95</h2>
          <div className="text-3xl font-bold mb-1">
            {health.p95_latency_ms.toFixed(0)}ms
          </div>
          <div className="text-xs text-gray-500">Meta: &lt;2000ms</div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Status das Integrações</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(health.integrations).map(([name, info]) => (
            <div key={name} className="p-4 border rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">{name.toUpperCase()}</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
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

      <div className="bg-gray-50 rounded-lg p-4 text-center text-sm text-gray-500">
        Última atualização: {new Date(health.timestamp).toLocaleString('pt-BR')}
      </div>
    </div>
  )
}
