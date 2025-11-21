#!/bin/bash

# Script de deploy para AWS
# Requisitos: AWS CLI configurado, Docker instalado, Terraform instalado

set -e

echo "🚀 Iniciando deploy para AWS..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variáveis
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REPOSITORY_BACKEND="hospital-assistant-backend"
ECR_REPOSITORY_FRONTEND="hospital-assistant-frontend"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo -e "${YELLOW}Região AWS: ${AWS_REGION}${NC}"
echo -e "${YELLOW}AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"

# 1. Login no ECR
echo -e "\n${GREEN}1. Fazendo login no Amazon ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# 2. Criar repositórios ECR se não existirem
echo -e "\n${GREEN}2. Criando repositórios ECR...${NC}"
aws ecr describe-repositories --repository-names ${ECR_REPOSITORY_BACKEND} --region ${AWS_REGION} || \
  aws ecr create-repository --repository-name ${ECR_REPOSITORY_BACKEND} --region ${AWS_REGION}
aws ecr describe-repositories --repository-names ${ECR_REPOSITORY_FRONTEND} --region ${AWS_REGION} || \
  aws ecr create-repository --repository-name ${ECR_REPOSITORY_FRONTEND} --region ${AWS_REGION}

# 3. Build e push do backend
echo -e "\n${GREEN}3. Build e push do backend...${NC}"
cd apps/backend-fastapi
docker build -t ${ECR_REPOSITORY_BACKEND}:latest .
docker tag ${ECR_REPOSITORY_BACKEND}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_BACKEND}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_BACKEND}:latest
cd ../..

# 4. Build e push do frontend
echo -e "\n${GREEN}4. Build e push do frontend...${NC}"
cd apps/frontend-next
docker build -t ${ECR_REPOSITORY_FRONTEND}:latest .
docker tag ${ECR_REPOSITORY_FRONTEND}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_FRONTEND}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_FRONTEND}:latest
cd ../..

# 5. Deploy com Terraform
echo -e "\n${GREEN}5. Deploy da infraestrutura com Terraform...${NC}"
cd infra/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
cd ../..

echo -e "\n${GREEN}✅ Deploy concluído com sucesso!${NC}"
echo -e "${YELLOW}URLs:${NC}"
echo -e "Backend: $(terraform -chdir=infra/terraform output -raw backend_url)"
echo -e "Frontend: $(terraform -chdir=infra/terraform output -raw frontend_url)"

