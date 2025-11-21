/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone', // Para Docker
  // Removemos rewrites globais - agora usamos rotas de API específicas
  // Isso evita erros de proxy quando backend não está rodando
}

module.exports = nextConfig
