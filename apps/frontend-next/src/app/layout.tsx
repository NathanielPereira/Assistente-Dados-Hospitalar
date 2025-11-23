import './globals.css'
import Link from 'next/link'
import Navbar from '@/components/Navbar'

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
        <Navbar />
        {children}
      </body>
    </html>
  )
}
