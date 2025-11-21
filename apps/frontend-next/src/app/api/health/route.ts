import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const healthUrl = `${apiUrl}/health`
    
    console.log(`[health] Tentando conectar em: ${healthUrl}`)
    
    const response = await fetch(healthUrl, {
      method: 'GET',
      signal: AbortSignal.timeout(5000), // Timeout de 5 segundos
    })
    
    if (response.ok) {
      const data = await response.json()
      console.log(`[health] Backend respondeu:`, data)
      return NextResponse.json({ 
        status: 'online',
        backendUrl: apiUrl,
        backendData: data
      })
    }
    
    console.log(`[health] Backend respondeu com status: ${response.status}`)
    return NextResponse.json({ 
      status: 'offline',
      backendUrl: apiUrl,
      error: `HTTP ${response.status}`
    }, { status: 503 })
  } catch (error) {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    console.error(`[health] Erro ao conectar:`, error)
    return NextResponse.json({ 
      status: 'offline',
      backendUrl: apiUrl,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 503 })
  }
}

