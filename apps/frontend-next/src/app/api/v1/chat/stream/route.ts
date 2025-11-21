import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const sessionId = searchParams.get('session_id')
  const prompt = searchParams.get('prompt')

  if (!sessionId || !prompt) {
    return new Response('Missing session_id or prompt', { status: 400 })
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const backendUrl = `${apiUrl}/v1/chat/stream?session_id=${sessionId}&prompt=${encodeURIComponent(prompt)}`

  try {
    const response = await fetch(backendUrl, {
      headers: {
        'Accept': 'text/event-stream',
      },
    })

    if (!response.ok) {
      return new Response(
        `data: ⚠️ Backend não está rodando. Inicie o servidor FastAPI na porta 8000.\n\n`,
        {
          status: 503,
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
          },
        }
      )
    }

    // Retorna o stream do backend
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    })
  } catch (error) {
    return new Response(
      `data: ⚠️ Erro ao conectar com backend: ${error instanceof Error ? error.message : 'Unknown error'}\n\n`,
      {
        status: 503,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      }
    )
  }
}

