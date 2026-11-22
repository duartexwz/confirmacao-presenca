# Confirmação de Presença API

API para gerenciar confirmações de presença do **Jantar de Noivado — Mayckon & Duda**.

## Arquitetura

O projeto segue uma arquitetura em camadas:

```
api/
├── main.py                        # Entrypoint da aplicação FastAPI
├── settings.py                    # Configurações via variáveis de ambiente
├── database.py                    # Pool de conexões asyncpg
├── schemas/
│   └── confirmacao_schemas.py     # Schemas Pydantic (validação/serialização)
├── repositories/
│   └── confirmacao_repository.py  # Queries SQL (acesso ao banco)
├── services/
│   └── confirmacao_service.py     # Lógica de negócio
└── routers/
    └── confirmacao_router.py      # Endpoints REST
```

**Fluxo:** `Router → Service → Repository → Banco de Dados`

## Requisitos

- Python 3.12+
- PostgreSQL

## Configuração

1. Copie o arquivo de exemplo e preencha com seus dados:

```bash
cp .env.example .env
```

2. Instale as dependências:

```bash
poetry install
```

3. Execute a API:

```bash
uvicorn api.main:app --reload
```

4. Acesse a documentação interativa:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Endpoints

| Método   | Rota                   | Descrição                        |
|----------|------------------------|----------------------------------|
| `GET`    | `/`                    | Health check                     |
| `POST`   | `/confirmacoes/`       | Confirmar presença               |
| `GET`    | `/confirmacoes/`       | Listar confirmações (paginado)   |
| `GET`    | `/confirmacoes/{id}`   | Buscar confirmação por UUID      |
| `DELETE` | `/confirmacoes/{id}`   | Remover confirmação              |
