# Confirmação de Presença — Jantar de Noivado (Mayckon & Duda)

Aplicação full-stack para gerenciar confirmações de presença do Jantar de Noivado & Chá de Panela.
Frontend em React + Vite e backend em FastAPI + PostgreSQL, com área administrativa protegida por JWT.

## Estrutura

```
confirmacao_presenca/
├── back/                 # API FastAPI
│   ├── api/
│   │   ├── main.py       # Entrypoint (FastAPI)
│   │   ├── settings.py   # Configurações via .env
│   │   ├── database.py   # Pool asyncpg
│   │   ├── security.py   # JWT, hash de senha, dependências
│   │   ├── routers/      # Endpoints (confirmacoes, admin, login)
│   │   ├── services/     # Lógica de negócio
│   │   ├── repositories/ # Acesso ao banco
│   │   └── schemas/      # Pydantic
│   ├── tests/            # Testes (pytest)
│   ├── requirements.txt
│   └── Dockerfile
├── front/                # React + Vite
│   └── src/
├── docker-compose.yml
└── vercel.json
```

## Requisitos

- Python 3.12+
- Node.js 18+
- PostgreSQL (ou Docker)

## Configuração

1. Copie o arquivo de ambiente:

```bash
cp .env.example .env
```

2. Ajuste as variáveis (banco, CORS, etc.). O admin padrão é criado automaticamente:
   - E-mail: `mayckonkennedy877@gmail.com`
   - Senha: `Mk@220525`

## Executando com Docker

```bash
docker compose up --build
```

- API: http://localhost:8000
- Frontend (nginx): http://localhost:3000

## Executando localmente

### Backend

```bash
cd back
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Acesse a documentação: http://localhost:8000/docs

### Frontend

```bash
cd front
npm install
npm run dev
```

Acesse: http://localhost:5173

## Endpoints principais

| Método   | Rota                          | Descrição                       |
|----------|-------------------------------|---------------------------------|
| `GET`    | `/`                           | Health check                    |
| `POST`   | `/api/v1/confirmacoes/`       | Confirmar presença              |
| `GET`    | `/api/v1/confirmacoes/`       | Listar confirmações (paginado)  |
| `GET`    | `/api/v1/confirmacoes/{id}`   | Buscar confirmação por UUID     |
| `DELETE` | `/api/v1/confirmacoes/{id}`   | Remover confirmação             |
| `POST`   | `/api/v1/login/`              | Login do administrador          |
| `GET`    | `/api/v1/admin/`              | Listar administradores          |
| `POST`   | `/api/v1/admin/`              | Cadastrar administrador         |
| `PUT`    | `/api/v1/admin/{id}`          | Atualizar administrador         |
| `DELETE` | `/api/v1/admin/{id}`          | Remover administrador           |

## Testes

```bash
cd back
pytest
```

## Área administrativa

Acesse o frontend e clique em **"Área do Admin"**. Faça login com as credenciais do administrador padrão.
No painel é possível visualizar as confirmações e gerenciar administradores.

## Deploy (Vercel)

O `vercel.json` na raiz configura dois serviços:

- `front`: Vite (build `npm run build`)
- `back`: FastAPI (`api.main:app`)

As rotas `/api/*` são direcionadas ao backend e as demais ao frontend.
Configure as variáveis de ambiente no projeto Vercel (banco, `SECRET_KEY`, `CORS_ORIGINS`, etc.).

## Licença

Projeto privado — Jantar de Noivado Mayckon & Duda.
