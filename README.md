# Lakebase Entra ID Explorer (MVP)

MVP con **backend FastAPI** (JWT validation Entra ID + endpoints de explorer hacia Lakebase/Postgres) y **frontend React/Vite** (MSAL login + UI básica para navegar schemas/tablas).

## Requisitos

- Node.js 18+
- Python 3.12+
- Credenciales para Entra ID (App Registrations de Frontend y API)
- Acceso a Lakebase por PostgreSQL wire-protocol (`LAKEBASE_HOST/DBNAME/...`)

## Variables de entorno

### Backend

1. Copia:

- `backend/.env.example` → `backend/.env`

2. Llena como mínimo:

- `CORS_ORIGINS` (ej. `http://localhost:5173`)
- `LAKEBASE_HOST`, `LAKEBASE_DBNAME` (y `LAKEBASE_PORT` si aplica)
- `ENTRA_TENANT_ID`
- `ENTRA_API_AUDIENCE`
- `ENTRA_ISSUER`

### Frontend

1. Copia:

- `frontend/.env.example` → `frontend/.env`

2. Llena:

- `VITE_ENTRA_CLIENT_ID`
- `VITE_ENTRA_AUTHORITY` (ej. `https://login.microsoftonline.com/<tenantId>`)
- `VITE_ENTRA_REDIRECT_URI` (ej. `http://localhost:5173`)
- `VITE_API_BASE_URL` (ej. `http://localhost:8000`)
- `VITE_API_SCOPES` (ej. `api://<backend-app-id>/access_as_user`)

## Correr local

### Backend

```bat
cd backend
uv run uvicorn backend.app.main:app --reload --port 8000
```

### Frontend

```bat
cd frontend
npm install
npm run dev
```

## Endpoints principales

- `GET /api/health` público
- `GET /api/me` protegido (retorna claims permitidos)
- `GET /api/explorer/schemas` protegido
- `GET /api/explorer/schemas/{schema}/tables` protegido
- `GET /api/explorer/schemas/{schema}/tables/{table}/describe` protegido
- `GET /api/explorer/schemas/{schema}/tables/{table}/preview?limit=20` protegido

## Notas de seguridad

- No commitear `backend/.env` ni `frontend/.env`.
- No imprimir tokens en logs (frontend/back).
