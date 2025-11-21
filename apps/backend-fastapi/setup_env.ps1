# Script para configurar arquivo .env
# Execute: .\setup_env.ps1

$envContent = @"
# Database
DATABASE_URL=postgresql://neondb_owner:npg_15HewNKxEdgB@ep-gentle-morning-aci29uzb-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# OpenAI (adicionar quando tiver a chave)
OPENAI_API_KEY=

# S3 (adicionar quando configurar)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=sa-east-1
S3_BUCKET_NAME=

# Redis (adicionar quando configurar)
REDIS_URL=

# Environment
ENVIRONMENT=development
"@

$envContent | Out-File -FilePath ".env" -Encoding utf8
Write-Host "✅ Arquivo .env criado com sucesso!"


