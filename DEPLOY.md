# 🚀 Guia de Deploy - Hospital Data Assistant

Este guia detalha como fazer deploy do projeto na AWS.

## 📋 Pré-requisitos

1. **AWS Account** com permissões adequadas
2. **AWS CLI** instalado e configurado
3. **Terraform** >= 1.0 instalado
4. **Docker** instalado
5. **Credenciais AWS** configuradas (`aws configure`)

## 🔧 Configuração Inicial

### 1. Configure AWS CLI

```bash
aws configure
# AWS Access Key ID: [sua-chave]
# AWS Secret Access Key: [sua-chave-secreta]
# Default region name: us-east-1
# Default output format: json
```

### 2. Configure Variáveis de Ambiente

Crie um arquivo `infra/terraform/terraform.tfvars`:

```hcl
aws_region = "us-east-1"
database_url = "postgresql://user:pass@host/db"
openai_api_key = "sk-..."
```

**⚠️ IMPORTANTE**: Adicione `terraform.tfvars` ao `.gitignore` para não commitar secrets!

### 3. Configure Permissões IAM

Certifique-se de que seu usuário AWS tem as seguintes permissões:
- EC2 (VPC, Security Groups, Subnets)
- ECS (Cluster, Services, Task Definitions)
- ECR (Repositories, Push/Pull)
- IAM (Roles, Policies)
- CloudWatch (Log Groups)
- Application Load Balancer

## 🐳 Build e Push das Imagens Docker

### Opção 1: Script Automatizado

```bash
chmod +x infra/aws/deploy.sh
./infra/aws/deploy.sh
```

### Opção 2: Manual

```bash
# 1. Login no ECR
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-east-1"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. Criar repositórios ECR
aws ecr create-repository --repository-name hospital-assistant-backend --region $AWS_REGION
aws ecr create-repository --repository-name hospital-assistant-frontend --region $AWS_REGION

# 3. Build e push backend
cd apps/backend-fastapi
docker build -t hospital-assistant-backend:latest .
docker tag hospital-assistant-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-backend:latest

# 4. Build e push frontend
cd ../frontend-next
docker build -t hospital-assistant-frontend:latest .
docker tag hospital-assistant-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-frontend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-assistant-frontend:latest
```

## 🏗️ Deploy da Infraestrutura com Terraform

```bash
cd infra/terraform

# 1. Inicializar Terraform
terraform init

# 2. Planejar mudanças
terraform plan

# 3. Aplicar infraestrutura
terraform apply

# 4. Ver outputs (URLs)
terraform output
```

## ✅ Verificação do Deploy

Após o deploy, você deve ter:

1. **VPC** com subnets públicas e privadas
2. **ECS Cluster** criado
3. **ECR Repositories** com imagens
4. **ECS Services** rodando (backend e frontend)
5. **Application Load Balancer** com DNS público
6. **CloudWatch Log Groups** para logs

### Verificar Status dos Services

```bash
# Status do cluster
aws ecs describe-clusters --clusters hospital-assistant-cluster

# Status dos services
aws ecs describe-services --cluster hospital-assistant-cluster --services hospital-assistant-backend hospital-assistant-frontend

# Logs do backend
aws logs tail /ecs/hospital-assistant-backend --follow

# Logs do frontend
aws logs tail /ecs/hospital-assistant-frontend --follow
```

## 🔗 URLs de Acesso

Após o deploy, você pode acessar:

- **Backend API**: `http://[ALB-DNS]/health`
- **Frontend**: URL será exibida no output do Terraform

## 🔄 Atualizações

Para atualizar o código:

```bash
# 1. Rebuild e push das imagens
./infra/aws/deploy.sh

# 2. Force new deployment no ECS
aws ecs update-service --cluster hospital-assistant-cluster --service hospital-assistant-backend --force-new-deployment
aws ecs update-service --cluster hospital-assistant-cluster --service hospital-assistant-frontend --force-new-deployment
```

## 🗑️ Destruir Infraestrutura

```bash
cd infra/terraform
terraform destroy
```

**⚠️ ATENÇÃO**: Isso irá deletar TODA a infraestrutura criada!

## 💰 Estimativa de Custos AWS

Com a configuração atual (Fargate, 1 task cada):

- **ECS Fargate**: ~$30-50/mês (dependendo do uso)
- **ECR**: Gratuito (até 500MB/mês)
- **ALB**: ~$16/mês
- **CloudWatch Logs**: ~$0.50/GB
- **VPC**: Gratuito
- **Data Transfer**: Variável

**Total estimado**: ~$50-70/mês para ambiente de desenvolvimento/teste

## 🐛 Troubleshooting

### Erro: "No space left on device"
```bash
# Limpar imagens Docker antigas
docker system prune -a
```

### Erro: "Task failed to start"
```bash
# Verificar logs do CloudWatch
aws logs tail /ecs/hospital-assistant-backend --follow
```

### Erro: "Cannot pull image"
```bash
# Verificar permissões ECR
aws ecr describe-repositories
# Verificar IAM role do ECS task
```

### Erro: "Health check failed"
```bash
# Verificar security groups
# Verificar se a porta está correta
# Verificar se o health endpoint está funcionando
```

## 📚 Recursos Adicionais

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

