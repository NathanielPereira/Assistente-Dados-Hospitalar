import { NextResponse } from 'next/server'

export async function GET() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const url = `${apiUrl}/v1/observability/health`
  
  try {
    console.log(`[observability-api] Fetching from: ${url}`)
    const response = await fetch(url, {
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
      },
    })

    console.log(`[observability-api] Response status: ${response.status}`)

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    console.log(`[observability-api] Data received:`, JSON.stringify(data).substring(0, 200))
    return NextResponse.json(data)
  } catch (error: any) {
    console.error(`[observability-api] Error:`, error.message)
    // Retorna dados mínimos se backend não está rodando
    return NextResponse.json({
      status: 'degraded',
      timestamp: new Date().toISOString(),
      uptime_percent: 0,
      p95_latency_ms: 0,
      database: {
        name: 'PostgreSQL (NeonDB)',
        status: 'disconnected',
        version: 'unknown',
        last_check: new Date().toISOString(),
        healthy: false
      },
      llm_providers: [],
      llm_summary: {
        total_providers: 0,
        active_providers: 0,
        status: 'degraded',
        last_check: new Date().toISOString()
      },
      metrics: {
        p95_latency_ms: 0,
        avg_latency_ms: 0,
        total_requests: 0,
        successful_requests: 0,
        failed_requests: 0
      },
      features: {
        read_only_mode: true,
        smart_detection: false,
        cache_enabled: false
      }
    })
  }
}

