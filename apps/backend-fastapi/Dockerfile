FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN pip install poetry==1.7.1

# Configura Poetry para não criar ambiente virtual (usa o sistema)
RUN poetry config virtualenvs.create false

# Copia arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Instala dependências
RUN poetry install --no-dev --no-interaction --no-ansi

# Copia código da aplicação
COPY src/ ./src/
COPY infra/scripts/schema_layers.sql ./infra/scripts/

# Expõe porta
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

