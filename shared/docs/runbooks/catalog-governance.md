# Governança do Catálogo DocumentCorpus

## Metadados Obrigatórios

Cada documento no catálogo DEVE conter:
- origin: Fonte do documento (ex: "Protocolo UTI", "Manual de Estoque")
- ersion: Versão semântica (ex: "1.0", "2.1")
- classification: Nível de sigilo (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)
- owner: Equipe/proprietário responsável
- created_at: Timestamp de criação
- s3_key: Chave no bucket S3
- hash: Hash SHA-256 do conteúdo

## Políticas de Acesso por Papel

- **CONSULTOR**: Acesso a PUBLIC + INTERNAL
- **ANALISTA**: Acesso a PUBLIC + INTERNAL + CONFIDENTIAL
- **COMPLIANCE**: Acesso total (incluindo RESTRICTED)

## Sincronização

O catálogo é sincronizado automaticamente ao carregar documentos via load_documents.py.
