# Script para adicionar OPENAI_API_KEY ao .env
$envFile = ".env"
$apiKey = "SUA_CHAVE_OPENAI_AQUI"

# Verifica se o arquivo existe
if (Test-Path $envFile) {
    # Lê o conteúdo atual
    $content = Get-Content $envFile -Raw
    
    # Verifica se OPENAI_API_KEY já existe
    if ($content -match "OPENAI_API_KEY=") {
        # Substitui a linha existente
        $content = $content -replace "OPENAI_API_KEY=.*", "OPENAI_API_KEY=$apiKey"
        Set-Content -Path $envFile -Value $content -NoNewline
        Write-Host "[OK] OPENAI_API_KEY atualizada no .env"
    } else {
        # Adiciona no final
        Add-Content -Path $envFile -Value "`nOPENAI_API_KEY=$apiKey"
        Write-Host "[OK] OPENAI_API_KEY adicionada ao .env"
    }
} else {
    # Cria o arquivo se não existir
    Set-Content -Path $envFile -Value "OPENAI_API_KEY=$apiKey"
    Write-Host "[OK] Arquivo .env criado com OPENAI_API_KEY"
}

Write-Host ""
Write-Host "Pronto! Reinicie o servidor FastAPI para aplicar as mudancas."

