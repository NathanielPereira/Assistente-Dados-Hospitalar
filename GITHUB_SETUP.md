# 📦 Guia de Setup no GitHub

Este guia explica como preparar e publicar o projeto no GitHub.

## 🚀 Passos para Publicar

### 1. Criar Repositório no GitHub

1. Acesse [GitHub](https://github.com)
2. Clique em "New repository"
3. Nome: `hospital-data-assistant`
4. Descrição: "AI-Powered Healthcare Analytics Platform with LangChain SQLAgent and RAG"
5. Público ou Privado (sua escolha)
6. **NÃO** inicialize com README (já temos um)

### 2. Configurar Git Local

```bash
# Se ainda não inicializou o git
git init

# Adicionar remote
git remote add origin https://github.com/SEU-USUARIO/hospital-data-assistant.git

# Verificar
git remote -v
```

### 3. Primeiro Commit

```bash
# Adicionar todos os arquivos
git add .

# Commit inicial
git commit -m "Initial commit: Hospital Data Assistant - AI-powered healthcare analytics platform"

# Push para GitHub
git branch -M main
git push -u origin main
```

### 4. Configurar Secrets no GitHub (para CI/CD)

Se quiser usar GitHub Actions para deploy automático:

1. Vá em **Settings** > **Secrets and variables** > **Actions**
2. Adicione os seguintes secrets:
   - `AWS_ACCESS_KEY_ID`: Sua chave de acesso AWS
   - `AWS_SECRET_ACCESS_KEY`: Sua chave secreta AWS
   - `DATABASE_URL`: URL do banco de dados
   - `OPENAI_API_KEY`: Chave da API OpenAI

### 5. Configurar GitHub Pages (Opcional)

Para documentação:

1. Vá em **Settings** > **Pages**
2. Source: `main` branch
3. Folder: `/docs` (se tiver documentação estática)

## 📝 Arquivos Importantes

Certifique-se de que estes arquivos estão no repositório:

- ✅ `.gitignore` - Ignora arquivos sensíveis
- ✅ `README.md` - Documentação principal
- ✅ `README_EN.md` - English version
- ✅ `LICENSE` - Licença do projeto
- ✅ `CONTRIBUTING.md` - Guia de contribuição
- ✅ `DEPLOY.md` - Guia de deploy

## 🔒 Segurança

**NUNCA** commite:

- ❌ Arquivos `.env` ou `.env.local`
- ❌ Chaves de API ou secrets
- ❌ Credenciais AWS
- ❌ `terraform.tfvars` com secrets
- ❌ Arquivos de configuração com senhas

O `.gitignore` já está configurado para ignorar esses arquivos.

## 🏷️ Tags e Releases

Para criar uma release:

```bash
# Criar tag
git tag -a v1.0.0 -m "Release v1.0.0: Initial release"

# Push tag
git push origin v1.0.0
```

Depois, no GitHub:
1. Vá em **Releases**
2. Clique em **Draft a new release**
3. Selecione a tag `v1.0.0`
4. Adicione descrição
5. Publique

## 📊 Badges e Shields

Você pode adicionar badges ao README usando [shields.io](https://shields.io):

```markdown
![GitHub stars](https://img.shields.io/github/stars/seu-usuario/hospital-data-assistant)
![GitHub forks](https://img.shields.io/github/forks/seu-usuario/hospital-data-assistant)
![GitHub issues](https://img.shields.io/github/issues/seu-usuario/hospital-data-assistant)
```

## 🎯 Otimizações para LinkedIn

### 1. Descrição do Repositório

Use uma descrição clara e profissional:

```
🏥 AI-Powered Healthcare Analytics Platform | LangChain SQLAgent + RAG | Next.js + FastAPI | AWS Deployed | LGPD/HIPAA Compliant
```

### 2. Tópicos (Topics)

Adicione tópicos relevantes:
- `ai`
- `langchain`
- `nextjs`
- `fastapi`
- `healthcare`
- `aws`
- `docker`
- `terraform`
- `postgresql`
- `typescript`
- `python`
- `machine-learning`
- `nlp`
- `compliance`
- `lgpd`
- `hipaa`

### 3. README Profissional

O README já está otimizado para recrutadores, destacando:
- ✅ Tecnologias utilizadas
- ✅ Habilidades demonstradas
- ✅ Arquitetura do sistema
- ✅ Funcionalidades principais
- ✅ Deploy em produção

## 📈 Estatísticas e Insights

O GitHub fornece insights automáticos sobre:
- Commits
- Pull Requests
- Issues
- Contribuidores
- Linguagens utilizadas

Use esses dados para mostrar atividade e engajamento no projeto.

## 🔗 Links Úteis

- [GitHub Docs](https://docs.github.com)
- [GitHub Actions](https://docs.github.com/en/actions)
- [GitHub Pages](https://pages.github.com)
- [Shields.io](https://shields.io)

---

**Dica**: Mantenha o repositório atualizado com commits regulares e documentação clara para impressionar recrutadores! 🚀

