# 🚀 RevForce FastAPI

> Backend desenvolvido com **FastAPI**

> Gerenciador de dependências **Poetry**

> Servidor local **Uvicorn**

---

## 📂 Pré-requisitos

- Python 3.11+
- Poetry
- Docker

> Instalar Poetry (se não tiver):

```bash
pip install poetry
```

---

## ✅ Configurando o VS Code como editor default do git

### Instalando no Macos/Linux
```bash
# Instale o VS Code via brew
brew install --cask visual-studio-code

# Configure o git para abrir o VS Code
git config --global core.editor "code --wait $MERGED"
```

---

## ✅ Configurando o ambiente

```bash
# Clone o repositório
git clone https://tools.ages.pucrs.br/plataforma-de-marketing-e-sales-analytics/revforce-api.git
cd revforce-api

# Instale o ambiente virtual
python -m venv .venv

# Instale as dependências
poetry install

# Ative o ambiente virtual do Poetry
eval $(poetry env activate) 
```

### Atualizando uma dependência, ou adicionando uma no pyproject.toml
```bash
poetry lock
```

---

## Configurando Alembic
```bash
# Caso a pasta alembic ainda não tenha sido criada
alembic init -t async alembic 
```

> ⚠️ <span style="color:red">***IMPORTANTE:*** Atualizar a propriedade sqlalchemy.url com a url do banco de dados

### Usando Alembic

#### Gerando as revisões
```bash
alembic revision --autogenerate -m "adicione uma mensagem que faça sentido para o upgrade do banco de dados"

alembic upgrade <revision_id> #this id is retrieved by the previous command
```

#### Fazendo rollback das mudanças no banco de dados
```bash
# retorna o estado para a última revisão
alembic downgrade -1
```

---

## 🛢️ Configurando o banco de dados Postgres e o serviço em FastAPI local

### ✅ Usando Docker:

```bash
# Inicia um container com um banco postgres rodando no docker
docker run --name local-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=meubanco -p 5432:5432 -d postgres

# Gera a imagem docker que vai ser usada no comando seguinte
docker build --no-cache -t revforce-app .

# Roda um container com o projeto em FastAPI
docker run -d -p 8000:8000 -e DATABASE_URL="postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/meubanco" revforce-app
```

### ▶️ Executando o projeto localmente, fora do docker

```bash
uvicorn app.main:app --reload
```

> - O parâmetro `--reload` recarrega o servidor automaticamente a cada mudança.

Acesse:

- API rodando: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Documentação Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Documentação ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📦 Executando os testes

```bash
pytest
```

---

## ✏️ Contribuindo

Contribuições são muito bem-vindas!  
Envie Pull Requests 😊

---