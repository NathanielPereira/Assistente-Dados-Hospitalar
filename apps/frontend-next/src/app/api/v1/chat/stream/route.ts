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

  console.log(`[chat/stream] Tentando conectar em: ${backendUrl}`)
  console.log(`[chat/stream] NEXT_PUBLIC_API_URL: ${process.env.NEXT_PUBLIC_API_URL || 'NÃO CONFIGURADO'}`)

  try {
    const response = await fetch(backendUrl, {
      headers: {
        'Accept': 'text/event-stream',
      },
      signal: AbortSignal.timeout(30000), // 30 segundos timeout
    })

    if (!response.ok) {
      console.error(`[chat/stream] Backend respondeu com status: ${response.status}`)
      const errorText = await response.text().catch(() => 'Unknown error')
      return new Response(
        `data: ⚠️ Backend respondeu com erro (${response.status}). Verifique se está rodando em: ${apiUrl}\n\n`,
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
    console.error(`[chat/stream] Erro ao conectar:`, error)
    const errorMsg = error instanceof Error ? error.message : 'Unknown error'
    return new Response(
      `data: ⚠️ Erro ao conectar com backend: ${errorMsg}\n\ndata: URL tentada: ${backendUrl}\n\ndata: Verifique se NEXT_PUBLIC_API_URL está configurado no Vercel.\n\n`,
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

