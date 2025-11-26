'use client'

import { useState, useEffect } from 'react'

interface LLMProvider {
  name: string
  type: string
  status: string
  model: string
  enabled: boolean
  circuit_breaker_open: boolean
  consecutive_failures: number
}

interface HealthStatus {
  status: string
  uptime_percent: number
  p95_latency_ms: number
  timestamp: string
  database: {
    name: string
    status: string
    version: string
    last_check: string
    healthy: boolean
  }
  llm_providers: LLMProvider[]
  llm_summary: {
    total_providers: number
    active_providers: number
    status: string
    last_check: string
  }
  metrics: {
    p95_latency_ms: number
    avg_latency_ms: number
    total_requests: number
    successful_requests: number
    failed_requests: number
  }
  features: {
    read_only_mode: boolean
    smart_detection: boolean
    cache_enabled: boolean
  }
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
      const response = await fetch('/api/v1/observability/health', {
        cache: 'no-store',
        headers: {
          'Accept': 'application/json',
        },
      })
      if (!response.ok) {
        throw new Error(`Backend retornou ${response.status}`)
      }
      const data = await response.json()
      console.log('[observability] Data received:', data)
      setHealth(data)
      setError(null)
      setLoading(false)
    } catch (err: any) {
      console.error('[observability] Error:', err)
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

  const statusColor = health.status === 'healthy' ? 'text-green-600' : health.status === 'degraded' ? 'text-yellow-600' : 'text-red-600'
  const uptimeColor = health.uptime_percent >= 99 ? 'text-green-600' : health.uptime_percent >= 95 ? 'text-yellow-600' : 'text-red-600'

  return (
    <div className="container mx-auto p-4 sm:p-6 max-w-6xl">
      <div className="mb-4 sm:mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">📊 Observability Control Room</h1>
        <p className="text-sm sm:text-base text-gray-600">
          Monitoramento em tempo real da saúde do sistema. Métricas atualizadas a cada 5 segundos.
        </p>
      </div>

      {health.features?.read_only_mode && (
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
            {health.features?.read_only_mode ? 'Operando em modo limitado' : 'Sistema operacional'}
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
          {/* Database */}
          <div className="p-3 sm:p-4 border rounded-lg">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 mb-2">
              <h3 className="font-semibold text-sm sm:text-base">{health.database?.name || 'PostgreSQL (NeonDB)'}</h3>
              <span className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${
                health.database?.healthy 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {health.database?.healthy ? '✓ OK' : '✗ FALHA'}
              </span>
            </div>
            <div className="text-xs text-gray-500 mb-1">
              Status: {health.database?.status || 'unknown'}
            </div>
            {health.database?.version && (
              <div className="text-xs text-gray-500 mb-1 truncate" title={health.database.version}>
                Versão: {health.database.version.substring(0, 40)}...
              </div>
            )}
            {health.database?.last_check && (
              <div className="text-xs text-gray-500">
                Última verificação: {new Date(health.database.last_check).toLocaleTimeString('pt-BR')}
              </div>
            )}
          </div>

          {/* LLM Summary */}
          <div className="p-3 sm:p-4 border rounded-lg">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 mb-2">
              <h3 className="font-semibold text-sm sm:text-base">LLM Providers</h3>
              <span className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${
                health.llm_summary?.status === 'healthy' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {health.llm_summary?.status === 'healthy' ? '✓ OK' : '⚠ DEGRADED'}
              </span>
            </div>
            <div className="text-xs text-gray-500 mb-1">
              Ativos: {health.llm_summary?.active_providers || 0} / {health.llm_summary?.total_providers || 0}
            </div>
            {health.llm_summary?.last_check && (
              <div className="text-xs text-gray-500">
                Última verificação: {new Date(health.llm_summary.last_check).toLocaleTimeString('pt-BR')}
              </div>
            )}
          </div>

          {/* Features */}
          <div className="p-3 sm:p-4 border rounded-lg">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 mb-2">
              <h3 className="font-semibold text-sm sm:text-base">Funcionalidades</h3>
              <span className="px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium bg-blue-100 text-blue-800">
                ✓ ATIVAS
              </span>
            </div>
            <div className="text-xs text-gray-500 space-y-1">
              <div>Smart Detection: {health.features?.smart_detection ? '✓' : '✗'}</div>
              <div>Cache: {health.features?.cache_enabled ? '✓' : '✗'}</div>
              <div>Read-Only: {health.features?.read_only_mode ? '⚠' : '✓'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* LLM Providers Detalhados */}
      {health.llm_providers && Array.isArray(health.llm_providers) && health.llm_providers.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 mb-4 sm:mb-6">
          <h2 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">Provedores de LLM</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            {health.llm_providers.map((provider, idx) => (
              <div key={idx} className="p-3 sm:p-4 border rounded-lg">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 mb-2">
                  <h3 className="font-semibold text-sm sm:text-base">{provider.name || 'Unknown'}</h3>
                  <span className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${
                    provider.status === 'healthy' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {provider.status === 'healthy' ? '✓ OK' : '✗ FALHA'}
                  </span>
                </div>
                {provider.type && (
                  <div className="text-xs text-gray-500 mb-1">
                    Tipo: {provider.type}
                  </div>
                )}
                {provider.model && (
                  <div className="text-xs text-gray-500 mb-1">
                    Modelo: {provider.model}
                  </div>
                )}
                {provider.circuit_breaker_open && (
                  <div className="text-xs text-yellow-600 mb-1">
                    ⚠ Circuit Breaker Aberto
                  </div>
                )}
                {provider.consecutive_failures > 0 && (
                  <div className="text-xs text-red-600">
                    Falhas consecutivas: {provider.consecutive_failures}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Métricas Detalhadas */}
      {health.metrics && (
        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 mb-4 sm:mb-6">
          <h2 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">Métricas de Performance</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
            <div className="p-3 border rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Latência Média</div>
              <div className="text-lg font-bold">{(health.metrics.avg_latency_ms || 0).toFixed(0)}ms</div>
            </div>
            <div className="p-3 border rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Total Requisições</div>
              <div className="text-lg font-bold">{health.metrics.total_requests || 0}</div>
            </div>
            <div className="p-3 border rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Sucessos</div>
              <div className="text-lg font-bold text-green-600">{health.metrics.successful_requests || 0}</div>
            </div>
            <div className="p-3 border rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Falhas</div>
              <div className="text-lg font-bold text-red-600">{health.metrics.failed_requests || 0}</div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-3 sm:p-4 text-center text-xs sm:text-sm text-gray-500">
        Última atualização: {new Date(health.timestamp).toLocaleString('pt-BR')}
      </div>
    </div>
  )
}
