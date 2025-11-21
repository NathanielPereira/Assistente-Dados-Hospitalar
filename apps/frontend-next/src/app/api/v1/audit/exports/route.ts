import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const params = new URLSearchParams()
    
    searchParams.forEach((value, key) => {
      params.append(key, value)
    })
    
    const response = await fetch(`${apiUrl}/v1/audit/exports?${params}`)

    if (!response.ok) {
      // Retorna array vazio se backend não está rodando
      return NextResponse.json({ audit_entries: [] })
    }

    return NextResponse.json(await response.json())
  } catch (error) {
    // Retorna array vazio se backend não está rodando
    return NextResponse.json({ audit_entries: [] })
  }
}

