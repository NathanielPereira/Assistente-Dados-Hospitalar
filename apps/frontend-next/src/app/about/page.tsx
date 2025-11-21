export default function AboutPage() {
  return (
    <div className="container mx-auto p-8 max-w-4xl">
      <h1 className="text-4xl font-bold mb-6">🏥 Assistente de Dados Hospitalar</h1>
      
      <div className="prose max-w-none">
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">O que é este projeto?</h2>
          <p className="text-lg text-gray-700 mb-4">
            Um <strong>assistente inteligente de dados</strong> desenvolvido para hospitais, 
            que combina <strong>Inteligência Artificial</strong> (LangChain) com acesso a 
            <strong> dados estruturados</strong> (PostgreSQL) e <strong>documentos</strong> (RAG).
          </p>
          <p className="text-gray-700">
            Permite que profissionais de saúde e analistas façam perguntas em linguagem natural 
            e recebam respostas precisas, combinando informações de múltiplas fontes com 
            <strong> rastreabilidade completa</strong> e <strong>compliance LGPD/HIPAA</strong>.
          </p>
        </section>

        <section className="mb-8 bg-blue-50 p-6 rounded-lg">
          <h2 className="text-2xl font-semibold mb-4">🎯 Funcionalidades Principais</h2>
          
          <div className="space-y-4">
            <div className="bg-white p-4 rounded shadow-sm">
              <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
                💬 <span>Chat Clínico Unificado</span>
              </h3>
              <p className="text-gray-700">
                Faça perguntas como <em>"Qual a taxa de ocupação da UTI pediátrica?"</em> e receba 
                respostas em tempo real que combinam:
              </p>
              <ul className="list-disc list-inside mt-2 text-gray-700 space-y-1">
                <li>Dados estruturados do banco (calculados via SQL)</li>
                <li>Protocolos e documentos hospitalares (via RAG)</li>
                <li>SQL executado visível para auditoria</li>
                <li>Citações dos documentos consultados</li>
              </ul>
            </div>

            <div className="bg-white p-4 rounded shadow-sm">
              <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
                🔧 <span>SQL Workbench Assistido</span>
              </h3>
              <p className="text-gray-700">
                Para analistas de dados que precisam criar consultas SQL complexas:
              </p>
              <ul className="list-disc list-inside mt-2 text-gray-700 space-y-1">
                <li>Descreva o que você quer em português</li>
                <li>Receba sugestões de SQL comentadas automaticamente</li>
                <li>Edite e aprimore antes de executar</li>
                <li>Receba resumos textuais dos resultados</li>
                <li>Tudo rastreado para auditoria</li>
              </ul>
            </div>

            <div className="bg-white p-4 rounded shadow-sm">
              <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
                📋 <span>Painel de Compliance</span>
              </h3>
              <p className="text-gray-700">
                Para oficiais de compliance e auditores:
              </p>
              <ul className="list-disc list-inside mt-2 text-gray-700 space-y-1">
                <li>Visualize todas as interações do sistema</li>
                <li>Exporte trilhas de auditoria em CSV/JSON</li>
                <li>Verifique bases legais (LGPD/HIPAA)</li>
                <li>Rastreie quem acessou o quê e quando</li>
              </ul>
            </div>

            <div className="bg-white p-4 rounded shadow-sm">
              <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
                📊 <span>Observability Control Room</span>
              </h3>
              <p className="text-gray-700">
                Monitoramento em tempo real do sistema:
              </p>
              <ul className="list-disc list-inside mt-2 text-gray-700 space-y-1">
                <li>Uptime e disponibilidade</li>
                <li>Latência p95 das requisições</li>
                <li>Status das integrações (banco, S3, RAG)</li>
                <li>Modo degradado quando há falhas</li>
                <li>Alertas automáticos</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="mb-8 bg-green-50 p-6 rounded-lg">
          <h2 className="text-2xl font-semibold mb-4">🔒 Segurança e Compliance</h2>
          <ul className="space-y-2 text-gray-700">
            <li>✅ <strong>Criptografia ponta a ponta</strong> (AES-256 + TLS 1.3)</li>
            <li>✅ <strong>Mascaramento de dados sensíveis</strong> (PII nunca exposto)</li>
            <li>✅ <strong>Trilhas de auditoria imutáveis</strong> com hashes verificáveis</li>
            <li>✅ <strong>Base legal documentada</strong> para cada acesso (LGPD/HIPAA)</li>
            <li>✅ <strong>Camadas de dados segregadas</strong> (bronze/prata/ouro)</li>
            <li>✅ <strong>Modo degradado automático</strong> em caso de falhas</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">🛠️ Tecnologias</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-3 rounded">
              <strong>Frontend:</strong> Next.js 14 + React
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <strong>Backend:</strong> FastAPI + Python
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <strong>IA:</strong> LangChain + SQLAgent
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <strong>Banco:</strong> PostgreSQL (NeonDB)
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <strong>RAG:</strong> Documentos S3
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <strong>Cache:</strong> Redis
            </div>
          </div>
        </section>

        <section className="bg-yellow-50 p-6 rounded-lg">
          <h2 className="text-2xl font-semibold mb-4">⚠️ Importante</h2>
          <p className="text-gray-700 mb-2">
            Este é um <strong>projeto demonstrativo</strong> usando <strong>dados fictícios</strong>.
          </p>
          <p className="text-gray-700">
            Todos os dados hospitalares são sintéticos e criados apenas para demonstração 
            das capacidades técnicas do sistema.
          </p>
        </section>
      </div>
    </div>
  )
}

