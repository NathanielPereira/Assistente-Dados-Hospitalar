import './globals.css'
import Link from 'next/link'

export const metadata = {
  title: 'Assistente de Dados Hospitalar',
  description: 'Sistema de assistência de dados com IA',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b mb-4">
          <div className="container mx-auto px-4 py-3">
            <div className="flex gap-4">
              <Link href="/" className="font-bold text-xl">🏥 Assistente Hospitalar</Link>
              <Link href="/about" className="px-3 py-1 hover:bg-gray-100 rounded">Sobre</Link>
              <Link href="/chat" className="px-3 py-1 hover:bg-gray-100 rounded">💬 Chat</Link>
              <Link href="/sql-workbench" className="px-3 py-1 hover:bg-gray-100 rounded">🔧 SQL</Link>
              <Link href="/compliance" className="px-3 py-1 hover:bg-gray-100 rounded">📋 Compliance</Link>
              <Link href="/observability" className="px-3 py-1 hover:bg-gray-100 rounded">📊 Observability</Link>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  )
}
