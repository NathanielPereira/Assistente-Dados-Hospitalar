# 🚀 AWS Deploy - Quick Start

Guia rápido para fazer deploy na AWS em **15 minutos**.

---

## ✅ Pré-requisitos (5 minutos)

### 1. Instalar Ferramentas

```powershell
# AWS CLI
winget install Amazon.AWSCLI

# Terraform
choco install terraform

# Docker Desktop (se não tiver)
# Baixe de: https://www.docker.com/products/docker-desktop
```

### 2. Criar Conta AWS e Credenciais

1. Acesse: https://aws.amazon.com
2. Crie conta (precisa de cartão, mas tem free tier)
3. Vá em **IAM** > **Users** > **Create user**
4. Nome: `hospital-deploy`
5. Permissões: Adicione `AdministratorAccess` (temporário, para facilitar)
6. Crie **Access Key** e copie:
   - Access Key ID
   - Secret Access Key

### 3. Configurar AWS CLI

```powershell
aws configure
# Cole as credenciais
# Region: us-east-1
# Output: json
```

---

## 🐳 Passo 1: Build e Push Docker (5 minutos)

### Opção A: Script Automatizado (Recomendado)

```powershell
.\infra\aws\deploy.ps1
```

### Opção B: Manual

```powershell
# 1. Obter Account ID
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$AWS_REGION = "us-east-1"

# 2. Login ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# 3. Criar repositórios
aws ecr create-repository --repository-name hospital-assistant-backend --region $AWS_REGION
aws ecr create-repository --repository-name hospital-assistant-frontend --region $AWS_REGION

# 4. Build e push backend
cd apps/backend-fastapi
docker build -t hospital-assistant-backend:latest .
docker tag hospital-assistant-backend:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-backend:latest"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-backend:latest"
cd ../..

# 5. Build e push frontend
cd apps/frontend-next
docker build -t hospital-assistant-frontend:latest .
docker tag hospital-assistant-frontend:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-frontend:latest"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-frontend:latest"
cd ../..
```

---

## 🏗️ Passo 2: Configurar Terraform (2 minutos)

### 2.1 Criar arquivo de variáveis

Crie `infra/terraform/terraform.tfvars`:

```hcl
aws_region = "us-east-1"
database_url = "postgresql://neondb_owner:npg_15HewNKxEdgB@ep-gentle-morning-aci29uzb-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
openai_api_key = "sua-chave-openai-aqui"
```

⚠️ **IMPORTANTE**: Adicione ao `.gitignore`:
```
infra/terraform/terraform.tfvars
```

### 2.2 Inicializar Terraform

```powershell
cd infra/terraform
terraform init
```

---

## 🚀 Passo 3: Deploy (5 minutos)

### 3.1 Planejar

```powershell
terraform plan
```

Revise o que será criado (VPC, ECS, ALB, etc.)

### 3.2 Aplicar

```powershell
terraform apply
```

Digite `yes` quando perguntado.

⏱️ **Aguarde 5-10 minutos** enquanto cria a infraestrutura.

### 3.3 Obter URLs

```powershell
terraform output
```

Você verá:
- `backend_url`: URL do backend
- `frontend_url`: URL do frontend

---

## ✅ Passo 4: Verificar (3 minutos)

### 4.1 Testar Backend

```powershell
# Use a URL do terraform output
curl http://[ALB-DNS]/health
```

Deve retornar: `{"status":"healthy","database":"connected"}`

### 4.2 Verificar Logs

```powershell
# Backend
aws logs tail /ecs/hospital-assistant-backend --follow --region us-east-1

# Frontend
aws logs tail /ecs/hospital-assistant-frontend --follow --region us-east-1
```

### 4.3 Testar Frontend

Acesse a URL do `frontend_url` do `terraform output`.

---

## 🔄 Atualizar Código

Quando fizer mudanças:

```powershell
# 1. Build e push novas imagens
.\infra\aws\deploy.ps1

# 2. Force new deployment
aws ecs update-service --cluster hospital-assistant-cluster --service hospital-assistant-backend --force-new-deployment --region us-east-1
aws ecs update-service --cluster hospital-assistant-cluster --service hospital-assistant-frontend --force-new-deployment --region us-east-1
```

---

## 💰 Custos

### Free Tier (12 meses)
- ✅ 750 horas/mês ECS Fargate (suficiente!)
- ✅ 750 horas/mês ALB
- ✅ 5GB CloudWatch Logs

### Após Free Tier
- ~$50-70/mês (1 task cada serviço)

---

## 🗑️ Limpar (Se Precisar)

```powershell
cd infra/terraform
terraform destroy
```

⚠️ **CUIDADO**: Isso deleta TUDO!

---

## 📚 Documentação Completa

Veja `AWS_DEPLOY_STEP_BY_STEP.md` para guia detalhado.

---

**🎉 Pronto! Seu projeto está na AWS!**

