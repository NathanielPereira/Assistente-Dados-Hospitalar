import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(2000), // Timeout de 2 segundos
    })
    
    if (response.ok) {
      return NextResponse.json({ status: 'online' })
    }
    return NextResponse.json({ status: 'offline' }, { status: 503 })
  } catch (error) {
    // Backend não está rodando - retorna offline sem erro
    return NextResponse.json({ status: 'offline' }, { status: 503 })
  }
}

