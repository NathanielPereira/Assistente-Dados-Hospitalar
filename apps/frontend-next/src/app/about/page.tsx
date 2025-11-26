export default function AboutPage() {
  return (
    <div className="container mx-auto p-4 sm:p-6 md:p-8 max-w-5xl">
      <div className="text-center mb-8">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          🏥 Assistente de Dados Hospitalar
        </h1>
        <p className="text-lg sm:text-xl text-gray-700 max-w-2xl mx-auto">
          Sistema inteligente que combina <strong>IA (LangChain)</strong> com <strong>dados estruturados</strong> e <strong>documentos</strong> para respostas precisas em linguagem natural.
        </p>
      </div>
      
      <div className="space-y-6">
        {/* Status do Projeto */}
        <section className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-200">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <span className="text-2xl">🚀</span>
            <span>Status do Projeto</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h3 className="font-semibold text-green-700 mb-2 flex items-center gap-2">
                <span className="text-xl">✅</span>
                <span>Em Produção</span>
              </h3>
              <ul className="text-sm text-gray-700 space-y-1 ml-7">
                <li>• <strong>Frontend:</strong> Hospedado na <a href="https://vercel.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Vercel</a></li>
                <li>• <strong>Backend:</strong> Hospedado no <a href="https://render.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Render</a></li>
                <li>• <strong>Banco de Dados:</strong> NeonDB (PostgreSQL serverless)</li>
                <li>• <strong>Deploy:</strong> Automático via GitHub</li>
              </ul>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h3 className="font-semibold text-orange-700 mb-2 flex items-center gap-2">
                <span className="text-xl">🔄</span>
                <span>Em Desenvolvimento</span>
              </h3>
              <ul className="text-sm text-gray-700 space-y-1 ml-7">
                <li>• Integração RAG completa (documentos S3)</li>
                <li>• Cache Redis para otimização</li>
                <li>• Autenticação e autorização de usuários</li>
                <li>• Dashboard de métricas avançado</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Funcionalidades */}
        <section className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            <span>Funcionalidades Principais</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 p-5 rounded-lg border border-blue-100">
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <span className="text-2xl">💬</span>
                <span>Chat Clínico</span>
              </h3>
              <p className="text-gray-700 text-sm mb-3">
                Faça perguntas em português e receba respostas combinando dados estruturados e documentos.
              </p>
              <ul className="text-sm text-gray-700 space-y-1.5">
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Geração automática de SQL com IA</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Detecção inteligente de perguntas não respondíveis</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Cards visuais para métricas (ocupação, receita)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-orange-600 mt-1">○</span>
                  <span className="text-gray-500">Integração RAG (em desenvolvimento)</span>
                </li>
              </ul>
            </div>

            <div className="bg-green-50 p-5 rounded-lg border border-green-100">
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <span className="text-2xl">🔧</span>
                <span>SQL Workbench</span>
              </h3>
              <p className="text-gray-700 text-sm mb-3">
                Gere SQL automaticamente a partir de descrições em linguagem natural.
              </p>
              <ul className="text-sm text-gray-700 space-y-1.5">
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Sugestões de SQL comentadas</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Validação e aprovação antes de executar</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Resumos textuais dos resultados</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Rastreamento completo para auditoria</span>
                </li>
              </ul>
            </div>

            <div className="bg-purple-50 p-5 rounded-lg border border-purple-100">
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <span className="text-2xl">📋</span>
                <span>Compliance</span>
              </h3>
              <p className="text-gray-700 text-sm mb-3">
                Visualize e exporte trilhas de auditoria para LGPD/HIPAA.
              </p>
              <ul className="text-sm text-gray-700 space-y-1.5">
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Trilhas de auditoria completas</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Exportação CSV/JSON</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Rastreamento de todas as interações</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-orange-600 mt-1">○</span>
                  <span className="text-gray-500">Bases legais detalhadas (em desenvolvimento)</span>
                </li>
              </ul>
            </div>

            <div className="bg-orange-50 p-5 rounded-lg border border-orange-100">
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <span className="text-2xl">📊</span>
                <span>Observability</span>
              </h3>
              <p className="text-gray-700 text-sm mb-3">
                Monitore a saúde do sistema em tempo real.
              </p>
              <ul className="text-sm text-gray-700 space-y-1.5">
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Uptime e latência p95</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Status de integrações (DB, LLMs)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">✓</span>
                  <span>Modo degradado automático</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-orange-600 mt-1">○</span>
                  <span className="text-gray-500">Alertas automáticos (em desenvolvimento)</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Tecnologias */}
        <section className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <span className="text-2xl">🛠️</span>
            <span>Stack Tecnológico</span>
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <div className="font-semibold text-sm mb-1">Frontend</div>
              <div className="text-xs text-gray-600">Next.js 14 + React</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <div className="font-semibold text-sm mb-1">Backend</div>
              <div className="text-xs text-gray-600">FastAPI + Python</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <div className="font-semibold text-sm mb-1">IA</div>
              <div className="text-xs text-gray-600">LangChain + SQLAgent</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <div className="font-semibold text-sm mb-1">Banco</div>
              <div className="text-xs text-gray-600">PostgreSQL (NeonDB)</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <div className="font-semibold text-sm mb-1">Hospedagem</div>
              <div className="text-xs text-gray-600">Vercel + Render</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <div className="font-semibold text-sm mb-1">LLMs</div>
              <div className="text-xs text-gray-600">OpenAI, Gemini, Claude</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <div className="font-semibold text-sm mb-1">Cache</div>
              <div className="text-xs text-gray-600">In-memory (local)</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <div className="font-semibold text-sm mb-1">RAG</div>
              <div className="text-xs text-gray-600">Em desenvolvimento</div>
            </div>
          </div>
        </section>

        {/* Segurança */}
        <section className="bg-green-50 p-6 rounded-xl border border-green-200">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <span className="text-2xl">🔒</span>
            <span>Segurança e Compliance</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="flex items-start gap-2">
              <span className="text-green-600 mt-1">✓</span>
              <span className="text-sm text-gray-700"><strong>Trilhas de auditoria</strong> imutáveis</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 mt-1">✓</span>
              <span className="text-sm text-gray-700"><strong>Rastreamento completo</strong> de interações</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 mt-1">✓</span>
              <span className="text-sm text-gray-700"><strong>Exportação</strong> de trilhas (CSV/JSON)</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-orange-600 mt-1">○</span>
              <span className="text-sm text-gray-500"><strong>Criptografia</strong> ponta a ponta (planejado)</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-orange-600 mt-1">○</span>
              <span className="text-sm text-gray-500"><strong>Mascaramento de PII</strong> (planejado)</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-orange-600 mt-1">○</span>
              <span className="text-sm text-gray-500"><strong>Autenticação</strong> de usuários (planejado)</span>
            </div>
          </div>
        </section>

        {/* Aviso */}
        <section className="bg-yellow-50 p-6 rounded-xl border border-yellow-200">
          <h2 className="text-xl font-semibold mb-3 flex items-center gap-2">
            <span className="text-2xl">⚠️</span>
            <span>Importante</span>
          </h2>
          <p className="text-gray-700 text-sm mb-2">
            Este é um <strong>projeto demonstrativo</strong> usando <strong>dados fictícios</strong>.
          </p>
          <p className="text-gray-700 text-sm">
            Todos os dados hospitalares são sintéticos e criados apenas para demonstração das capacidades técnicas do sistema.
          </p>
        </section>

        {/* Links */}
        <section className="bg-blue-50 p-6 rounded-xl border border-blue-200 text-center">
          <h2 className="text-xl font-semibold mb-4">🔗 Links Úteis</h2>
          <div className="flex flex-wrap justify-center gap-4">
            <a 
              href="https://assistente-dados-hospitalar.vercel.app" 
              target="_blank" 
              rel="noopener noreferrer"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-semibold"
            >
              🌐 Aplicação em Produção
            </a>
            <a 
              href="https://assistente-dados-hospitalar.onrender.com/docs" 
              target="_blank" 
              rel="noopener noreferrer"
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-semibold"
            >
              📚 Documentação da API
            </a>
            <a 
              href="https://github.com/NathanielPereira/Assistente-Dados-Hospitalar" 
              target="_blank" 
              rel="noopener noreferrer"
              className="px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition text-sm font-semibold"
            >
              💻 Código no GitHub
            </a>
          </div>
        </section>
      </div>
    </div>
  )
}

