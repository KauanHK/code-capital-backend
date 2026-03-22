# SW Backend API

API MVP com FastAPI para CRUD completo de:
- category
- service
- client
- transaction

## Requisitos
- Python 3.11+
- Docker e Docker Compose

## Setup
1. Copie o arquivo de ambiente:

```bash
cp .env.example .env
```

2. Suba o PostgreSQL:

```bash
docker compose up -d postgres
```

3. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

4. Instale dependências:

```bash
pip install -r requirements.txt
```

5. Rode as migrações:

```bash
alembic upgrade head
```

6. Inicie a API:

```bash
uvicorn app.main:app --reload
```

## Documentação
- Swagger UI: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json

## Rotas CRUD
### Categories
- POST /categories
- GET /categories
- GET /categories/{category_id}
- PUT /categories/{category_id}
- DELETE /categories/{category_id}

### Services
- POST /services
- GET /services
- GET /services/{service_id}
- PUT /services/{service_id}
- DELETE /services/{service_id}

### Clients
- POST /clients
- GET /clients
- GET /clients/{client_id}
- PUT /clients/{client_id}
- DELETE /clients/{client_id}

### Transactions
- POST /transactions
- GET /transactions
- GET /transactions/{transaction_id}
- PUT /transactions/{transaction_id}
- DELETE /transactions/{transaction_id}

## Regras Implementadas
- Delecao bloqueada com dependencias para category, service e client (retorna 409).
- transaction.client_id opcional.
- Listagens retornam todos os registros (sem paginacao no MVP).
