import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/v1/observability/health`, {
      signal: AbortSignal.timeout(2000),
    })

    if (!response.ok) {
      // Retorna status mock se backend não está rodando
      return NextResponse.json({
        status: 'degraded',
        uptime_percent: 0,
        p95_latency_ms: 0,
        integrations: {
          neon: { status: 'offline', last_check: new Date().toISOString() },
          s3: { status: 'offline', last_check: new Date().toISOString() },
          redis: { status: 'offline', last_check: new Date().toISOString() },
        },
        degraded_mode: true,
        timestamp: new Date().toISOString(),
      })
    }

    return NextResponse.json(await response.json())
  } catch (error) {
    // Retorna status mock se backend não está rodando
    return NextResponse.json({
      status: 'degraded',
      uptime_percent: 0,
      p95_latency_ms: 0,
      integrations: {
        neon: { status: 'offline', last_check: new Date().toISOString() },
        s3: { status: 'offline', last_check: new Date().toISOString() },
        redis: { status: 'offline', last_check: new Date().toISOString() },
      },
      degraded_mode: true,
      timestamp: new Date().toISOString(),
    })
  }
}

