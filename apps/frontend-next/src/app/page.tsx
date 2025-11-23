import Link from 'next/link'

export default function Home() {
  return (
    <div className="container mx-auto p-4 sm:p-6 md:p-8">
      <div className="text-center mb-8 sm:mb-12">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3 sm:mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent px-2">
          Assistente de Dados Hospitalar
        </h1>
        <p className="text-base sm:text-lg md:text-xl mb-3 sm:mb-4 text-gray-700 px-2">
          IA que combina dados estruturados + documentos para respostas inteligentes
        </p>
        <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6 px-2">
          Faça perguntas em português e receba respostas precisas com rastreabilidade completa
        </p>
        <Link 
          href="/about" 
          className="inline-block px-4 sm:px-6 py-2 sm:py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm sm:text-base"
        >
          📖 Entenda como funciona
        </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
        <Link href="/chat" className="group p-4 sm:p-6 md:p-8 border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-lg transition-all bg-white">
          <div className="text-3xl sm:text-4xl mb-3 sm:mb-4">💬</div>
          <h2 className="text-xl sm:text-2xl font-bold mb-2 sm:mb-3 group-hover:text-blue-600 transition">Chat Clínico</h2>
          <p className="text-sm sm:text-base text-gray-600 mb-3 sm:mb-4">
            Faça perguntas em português sobre dados hospitalares e receba respostas combinando SQL + documentos
          </p>
          <div className="text-xs sm:text-sm text-blue-600 font-semibold group-hover:underline">
            Experimentar →
          </div>
        </Link>
        
        <Link href="/sql-workbench" className="group p-4 sm:p-6 md:p-8 border-2 border-gray-200 rounded-xl hover:border-green-500 hover:shadow-lg transition-all bg-white">
          <div className="text-3xl sm:text-4xl mb-3 sm:mb-4">🔧</div>
          <h2 className="text-xl sm:text-2xl font-bold mb-2 sm:mb-3 group-hover:text-green-600 transition">SQL Workbench</h2>
          <p className="text-sm sm:text-base text-gray-600 mb-3 sm:mb-4">
            Descreva o que você quer e receba SQL sugerido automaticamente. Edite, aprove e execute com segurança.
          </p>
          <div className="text-xs sm:text-sm text-green-600 font-semibold group-hover:underline">
            Experimentar →
          </div>
        </Link>
        
        <Link href="/compliance" className="group p-4 sm:p-6 md:p-8 border-2 border-gray-200 rounded-xl hover:border-purple-500 hover:shadow-lg transition-all bg-white">
          <div className="text-3xl sm:text-4xl mb-3 sm:mb-4">📋</div>
          <h2 className="text-xl sm:text-2xl font-bold mb-2 sm:mb-3 group-hover:text-purple-600 transition">Compliance</h2>
          <p className="text-sm sm:text-base text-gray-600 mb-3 sm:mb-4">
            Visualize e exporte todas as trilhas de auditoria. Totalmente rastreável e compatível com LGPD/HIPAA.
          </p>
          <div className="text-xs sm:text-sm text-purple-600 font-semibold group-hover:underline">
            Ver trilhas →
          </div>
        </Link>
        
        <Link href="/observability" className="group p-4 sm:p-6 md:p-8 border-2 border-gray-200 rounded-xl hover:border-orange-500 hover:shadow-lg transition-all bg-white">
          <div className="text-3xl sm:text-4xl mb-3 sm:mb-4">📊</div>
          <h2 className="text-xl sm:text-2xl font-bold mb-2 sm:mb-3 group-hover:text-orange-600 transition">Observability</h2>
          <p className="text-sm sm:text-base text-gray-600 mb-3 sm:mb-4">
            Monitore a saúde do sistema em tempo real: uptime, latência, integrações e modo degradado.
          </p>
          <div className="text-xs sm:text-sm text-orange-600 font-semibold group-hover:underline">
            Ver métricas →
          </div>
        </Link>
      </div>
      
      <div className="mt-8 sm:mt-12 p-4 sm:p-6 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="text-base sm:text-lg font-semibold mb-2">💡 Dica</h3>
        <p className="text-sm sm:text-base text-gray-700">
          Para funcionalidades completas, o <strong>backend precisa estar rodando</strong>. 
          Veja <Link href="/about" className="text-blue-600 underline">a página Sobre</Link> para entender melhor o projeto.
        </p>
      </div>
    </div>
  )
}

