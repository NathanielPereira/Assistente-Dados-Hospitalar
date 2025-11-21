import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    const response = await fetch(`${apiUrl}/v1/chat/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      // Se backend não está rodando, retorna sessão mock para desenvolvimento
      if (response.status === 0 || response.status >= 500) {
        return NextResponse.json({
          session_id: `mock-${Date.now()}`,
          user_id: body.user_id || 'demo-user',
          created_at: new Date().toISOString(),
        })
      }
      return NextResponse.json(
        { error: 'Failed to create session' },
        { status: response.status }
      )
    }

    return NextResponse.json(await response.json())
  } catch (error) {
    // Backend não está rodando - retorna sessão mock
    const body = await request.json().catch(() => ({}))
    return NextResponse.json({
      session_id: `mock-${Date.now()}`,
      user_id: body.user_id || 'demo-user',
      created_at: new Date().toISOString(),
    })
  }
}

