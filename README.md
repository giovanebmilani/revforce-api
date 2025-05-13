# 🚀 RevForce FastAPI

> Backend desenvolvido com **FastAPI**

> Gerenciador de dependências **Poetry**

> Servidor local **Uvicorn**

---

## 📂 Pré-requisitos

> Baixar e instalar python
- Python 3.11+ 
https://www.python.org/downloads/

> Baixar e instalar Docker Desktop
- Docker Desktop
https://www.docker.com

---

## ✅ Configurando o ambiente

Para executar a aplicação temos duas opções, configurar o ambiente python e o banco de dados manualmente (que pode ser feito com docker ou não), ou utilizar o `docker compose`.

Antes de tudo, clone o repositório e execute todos os comandos no diretório do projeto:

```bash
# Clone o repositório
git clone https://tools.ages.pucrs.br/plataforma-de-marketing-e-sales-analytics/revforce-api.git
cd revforce-api
```

### 🐋 Utilizando o `docker compose` (mais fácil)

O [`docker compose`](https://docs.docker.com/compose/) é uma ferramenta utlizada para definir e executar aplicações com múltiplos containers/serviços. Com ele, podemos escrever um arquivo de configuração YAML que define todos os serviços, volumes e redes do projeto, e o docker lida com o ciclo de vida de todos os componentes. 

Primeiramente, verifique se o compose está instalado ([documentação](https://docs.docker.com/compose/install/)):
> Se você tem o docker desktop, o compose vem junto por padrão

```bash
# Verifique a instalacao do docker compose
docker compose version
```

Com o compose instalado corretamente, basta executar o seguinte comando para executar toda a aplicação, banco de dados e api:

```bash
# Sobe todos os servicos necessarios
docker compose up
```

> Na primeira vez, a aplicação deve levar algum tempo para instalar todas as dependencias.

Para parar a aplicação, pressione `CTRL-C` no terminal. 

Para remover todos os dados do banco e começar do zero, execute (não deve ser necessário, mas é bom saber): 

```bash
# Apaga todos os dados
docker compose down -v
```

> NOTA: quando utilizar o `docker`/`docker compose` para rodar a aplicação, as dependencias não serão instaladas no seu sistema de arquivos, então a IDE não vai reconheçer os pacotes importados. Para resolver isso, execute os primeiros comandos da configuração manual, mas ainda use o `docker` para rodar a aplicação.

### 💪 Configuração manual


```bash
# Instale poetry (gerenciador de dependências)
pip install poetry

# Instale o ambiente virtual
python -m venv .venv

# Instale as dependências
poetry install

# Ative o ambiente virtual do Poetry
eval $(poetry env activate) 
```

### Apenas siga os passos dessa seção caso precise atualizar ou adicionar uma dependência no pyproject.toml

> Após adicionar a dependência no arquivo pyproject.toml, execute:
```bash
poetry install

poetry lock
```

---

## 🛢️ Configurando o banco de dados Postgres e o serviço em FastAPI local

### ✅ Usando Docker (Recomendado):

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

## Gerenciamento do banco de dados

### Usando Alembic

> ⚠️ <span style="color:red">***ATENÇÃO:*** Somente usamos o Alembic para atualizar as tabelas do banco de dados sem perder os dados já inseridos

#### Gerando as revisões
```bash
alembic revision --autogenerate -m "adicione uma mensagem que faça sentido para o upgrade do banco de dados"

alembic upgrade <revision_id> # revision_id é gerado pelo comando anterior, e aparecerá na pasta alembic/versions
```

#### Fazendo rollback das mudanças no banco de dados
```bash
# retorna o estado para a última revisão
alembic downgrade -1
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

### Instalando no windows

> Baixar e instalar o VS Code
https://code.visualstudio.com

> Abra um terminal e execute:
```bash
git config --global core.editor "code --wait"
```

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