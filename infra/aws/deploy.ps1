# Script de deploy para AWS (PowerShell)
# Requisitos: AWS CLI configurado, Docker instalado, Terraform instalado

$ErrorActionPreference = "Stop"

Write-Host "🚀 Iniciando deploy para AWS..." -ForegroundColor Green

# Variáveis
$AWS_REGION = if ($env:AWS_REGION) { $env:AWS_REGION } else { "us-east-1" }
$ECR_REPOSITORY_BACKEND = "hospital-assistant-backend"
$ECR_REPOSITORY_FRONTEND = "hospital-assistant-frontend"

try {
    $AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
    Write-Host "Região AWS: $AWS_REGION" -ForegroundColor Yellow
    Write-Host "AWS Account ID: $AWS_ACCOUNT_ID" -ForegroundColor Yellow

    # 1. Login no ECR
    Write-Host "`n1. Fazendo login no Amazon ECR..." -ForegroundColor Green
    $loginCommand = aws ecr get-login-password --region $AWS_REGION
    $loginCommand | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

    # 2. Criar repositórios ECR se não existirem
    Write-Host "`n2. Criando repositórios ECR..." -ForegroundColor Green
    try {
        aws ecr describe-repositories --repository-names $ECR_REPOSITORY_BACKEND --region $AWS_REGION 2>$null
    } catch {
        aws ecr create-repository --repository-name $ECR_REPOSITORY_BACKEND --region $AWS_REGION
    }
    
    try {
        aws ecr describe-repositories --repository-names $ECR_REPOSITORY_FRONTEND --region $AWS_REGION 2>$null
    } catch {
        aws ecr create-repository --repository-name $ECR_REPOSITORY_FRONTEND --region $AWS_REGION
    }

    # 3. Build e push do backend
    Write-Host "`n3. Build e push do backend..." -ForegroundColor Green
    Set-Location "apps/backend-fastapi"
    docker build -t "${ECR_REPOSITORY_BACKEND}:latest" .
    docker tag "${ECR_REPOSITORY_BACKEND}:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY_BACKEND}:latest"
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY_BACKEND}:latest"
    Set-Location "../.."

    # 4. Build e push do frontend
    Write-Host "`n4. Build e push do frontend..." -ForegroundColor Green
    Set-Location "apps/frontend-next"
    docker build -t "${ECR_REPOSITORY_FRONTEND}:latest" .
    docker tag "${ECR_REPOSITORY_FRONTEND}:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY_FRONTEND}:latest"
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY_FRONTEND}:latest"
    Set-Location "../.."

    # 5. Deploy com Terraform
    Write-Host "`n5. Deploy da infraestrutura com Terraform..." -ForegroundColor Green
    Set-Location "infra/terraform"
    terraform init
    terraform plan -out=tfplan
    terraform apply tfplan
    Set-Location "../.."

    Write-Host "`n✅ Deploy concluído com sucesso!" -ForegroundColor Green
    Write-Host "URLs:" -ForegroundColor Yellow
    terraform -chdir=infra/terraform output

} catch {
    Write-Host "`n❌ Erro durante o deploy: $_" -ForegroundColor Red
    exit 1
}

