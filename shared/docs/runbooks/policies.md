# Políticas de Segurança e Privacidade (LGPD/HIPAA Demo)

1. **Dados Utilizados**
   - Apenas datasets fictícios ou anonimizados irreversíveis.
   - Classificação de sigilo: Público, Interno, Restrito-Demo.

2. **Base Legal (Demo)**
   - Consentimento explícito para demonstrações públicas.
   - Interesses legítimos acadêmicos/educacionais para cenários internos.

3. **Controles Obrigatórios**
   - Criptografia AES-256 em repouso; TLS 1.3 com mTLS quando suportado.
   - Minimização de dados e mascaramento automático nas camadas Bronze/Prata.
   - Logs de auditoria imutáveis com retenção ≥ 2 anos em storage versionado.

4. **Processo de Revisão**
   - Toda história descreve finalidade, base legal e retenção antes de homologar.
   - Violação → abertura de `ComplianceFinding` com plano corretivo.

5. **Uso de Ambiente**
   - Proibido inserir dados reais.
   - Integrações externas só operam em modo read-only.

