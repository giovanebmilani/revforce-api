# Etapa 1: Build
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.8.2 python3 -

# Adiciona o diretório do Poetry ao PATH
ENV PATH="/root/.local/bin:$PATH"

# Verifica se o Poetry foi instalado corretamente
RUN echo $PATH && poetry --version

# Define o diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY pyproject.toml poetry.lock /app/

# Instala as dependências e plugins do Poetry
RUN poetry install --no-root

# Exporta as dependências para requirements.txt
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt

# Etapa 2: Execução
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o requirements.txt gerado na etapa anterior
COPY --from=builder /app/requirements.txt .

# Instala as dependências no container
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código-fonte
COPY . .

# Comando padrão: executa o servidor Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
