# 🚀 Deploy na AWS - Passo a Passo Completo

Este guia detalha como migrar do plano gratuito (Vercel + Render) para AWS com ECS Fargate.

---

## 📋 Pré-requisitos

### 1. Conta AWS

1. Acesse: https://aws.amazon.com
2. Crie uma conta (se não tiver)
3. ⚠️ **Importante**: Configure método de pagamento (AWS tem free tier, mas precisa de cartão)

### 2. Instalar Ferramentas

#### AWS CLI
```powershell
# Windows (PowerShell como Admin)
winget install Amazon.AWSCLI

# Ou baixe de: https://awscli.amazonaws.com/AWSCLIV2.msi
```

#### Terraform
```powershell
# Windows (Chocolatey)
choco install terraform

# Ou baixe de: https://developer.hashicorp.com/terraform/downloads
```

#### Docker Desktop
```powershell
# Baixe de: https://www.docker.com/products/docker-desktop
```

### 3. Configurar AWS CLI

```powershell
aws configure
```

Você precisará de:
- **AWS Access Key ID**: Criar em IAM > Users > Security credentials
- **AWS Secret Access Key**: Aparece apenas uma vez ao criar
- **Default region**: `us-east-1` (ou sua preferência)
- **Default output format**: `json`

---

## 🔑 Passo 1: Criar Credenciais AWS

### 1.1 Criar Usuário IAM

1. Acesse: https://console.aws.amazon.com/iam
2. Clique em **"Users"** > **"Create user"**
3. Nome: `hospital-assistant-deploy`
4. Selecione: **"Provide user access to the AWS Management Console"**
5. Clique em **"Next"**

### 1.2 Adicionar Permissões

1. Selecione: **"Attach policies directly"**
2. Adicione as políticas:
   - `AmazonEC2FullAccess`
   - `AmazonECS_FullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `IAMFullAccess` (ou criar role específica)
   - `CloudWatchFullAccess`
   - `ElasticLoadBalancingFullAccess`
3. Clique em **"Next"** > **"Create user"**

### 1.3 Criar Access Key

1. Clique no usuário criado
2. Vá em **"Security credentials"**
3. Clique em **"Create access key"**
4. Selecione: **"Command Line Interface (CLI)"**
5. Clique em **"Next"** > **"Create access key"**
6. ⚠️ **COPIE E SALVE**:
   - Access Key ID
   - Secret Access Key (aparece apenas uma vez!)

### 1.4 Configurar AWS CLI

```powershell
aws configure
# Cole as credenciais que você copiou
```

---

## 🐳 Passo 2: Preparar Imagens Docker

### 2.1 Login no Amazon ECR

```powershell
# Obter Account ID
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$AWS_REGION = "us-east-1"

# Login no ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
```

### 2.2 Criar Repositórios ECR

```powershell
# Backend
aws ecr create-repository --repository-name hospital-assistant-backend --region $AWS_REGION

# Frontend
aws ecr create-repository --repository-name hospital-assistant-frontend --region $AWS_REGION
```

### 2.3 Build e Push Backend

```powershell
cd apps/backend-fastapi

# Build
docker build -t hospital-assistant-backend:latest .

# Tag
docker tag hospital-assistant-backend:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-backend:latest"

# Push
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-backend:latest"
```

### 2.4 Build e Push Frontend

```powershell
cd apps/frontend-next

# Build
docker build -t hospital-assistant-frontend:latest .

# Tag
docker tag hospital-assistant-frontend:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-frontend:latest"

# Push
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-frontend:latest"
```

---

## 🏗️ Passo 3: Configurar Terraform

### 3.1 Criar Arquivo de Variáveis

Crie `infra/terraform/terraform.tfvars`:

```hcl
aws_region = "us-east-1"
database_url = "postgresql://neondb_owner:npg_15HewNKxEdgB@ep-gentle-morning-aci29uzb-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
openai_api_key = "sua-chave-openai-aqui"
```

⚠️ **IMPORTANTE**: Adicione `terraform.tfvars` ao `.gitignore` para não commitar secrets!

### 3.2 Inicializar Terraform

```powershell
cd infra/terraform
terraform init
```

### 3.3 Planejar Infraestrutura

```powershell
terraform plan
```

Isso mostra o que será criado:
- VPC e subnets
- Security Groups
- ECS Cluster
- ECS Services
- Application Load Balancer
- CloudWatch Log Groups

### 3.4 Aplicar Infraestrutura

```powershell
terraform apply
```

Digite `yes` quando perguntado.

Isso vai criar toda a infraestrutura (pode levar 5-10 minutos).

---

## ✅ Passo 4: Verificar Deploy

### 4.1 Obter URLs

```powershell
terraform output
```

Isso mostra:
- `backend_url`: URL do ALB para o backend
- `frontend_url`: URL do frontend (se configurado)

### 4.2 Testar Backend

```powershell
# Teste o health check
curl (terraform output -raw backend_url)/health
```

Deve retornar: `{"status":"healthy","database":"connected"}`

### 4.3 Verificar Logs

```powershell
# Logs do backend
aws logs tail /ecs/hospital-assistant-backend --follow --region us-east-1

# Logs do frontend
aws logs tail /ecs/hospital-assistant-frontend --follow --region us-east-1
```

---

## 🔄 Passo 5: Atualizar Frontend (Vercel)

### 5.1 Atualizar Variável no Vercel

1. Acesse: https://vercel.com/dashboard
2. Vá em **Settings** > **Environment Variables**
3. Atualize `NEXT_PUBLIC_API_URL`:
   - **Value**: Use a URL do ALB do backend (do `terraform output`)
4. Faça **Redeploy**

### 5.2 Ou Migrar Frontend para AWS

Se quiser migrar o frontend também para AWS:

1. O Terraform já cria o serviço do frontend
2. Use a URL do `terraform output`
3. Configure DNS (opcional) ou use a URL do ALB

---

## 💰 Estimativa de Custos AWS

### Free Tier (12 meses)
- ✅ **750 horas/mês** de ECS Fargate (suficiente para 1 task 24/7)
- ✅ **750 horas/mês** de ALB
- ✅ **5GB** de CloudWatch Logs
- ✅ **VPC** gratuito

### Após Free Tier
- **ECS Fargate**: ~$0.04/hora = ~$30/mês (1 task)
- **ALB**: ~$0.0225/hora = ~$16/mês
- **CloudWatch Logs**: ~$0.50/GB
- **Data Transfer**: Variável

**Total estimado**: ~$50-70/mês após free tier

---

## 🔧 Troubleshooting

### Erro: "Access Denied"
- Verifique se o usuário IAM tem as permissões corretas
- Verifique se as credenciais estão configuradas (`aws configure`)

### Erro: "Repository not found"
- Execute os comandos de criação de repositórios ECR primeiro
- Verifique se está na região correta

### Erro: "Task failed to start"
- Verifique os logs do CloudWatch
- Verifique se as variáveis de ambiente estão corretas no Terraform

### Backend não responde
- Verifique se o ALB está criado: `aws elbv2 describe-load-balancers`
- Verifique se o target group está saudável: `aws elbv2 describe-target-health`

---

## 📚 Próximos Passos

1. ✅ Configurar domínio customizado (opcional)
2. ✅ Configurar SSL/TLS com ACM
3. ✅ Configurar auto-scaling
4. ✅ Configurar backup do banco de dados
5. ✅ Configurar monitoramento com CloudWatch

---

## 🎯 Script Automatizado

Você também pode usar o script PowerShell que criamos:

```powershell
.\infra\aws\deploy.ps1
```

Mas primeiro configure:
- AWS CLI (`aws configure`)
- Arquivo `terraform.tfvars` com suas variáveis

---

**🚀 Pronto! Seu projeto estará rodando na AWS!**

