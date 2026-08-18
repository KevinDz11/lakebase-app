# Quickstart (MVP) — Lakebase Entra ID Explorer

Este quickstart cubre **solo** los prerequisitos de variables de entorno y cómo levantar el esqueleto de backend/frontend creado en Phase 1 (T001–T005).

## Requisitos previos

- Node.js 18+
- Python 3.11+ (el proyecto usa `uv`)
- Credenciales para `DefaultAzureCredential` (una de):
  - `az login` en el equipo
  - Visual Studio / VS Code Azure Account
  - Managed Identity (si aplica en hosting)

## Variables de entorno

### Backend (`backend/.env`)

1. Copiar:
   - `backend/.env.example` → `backend/.env`
2. Completar como mínimo:

- `CORS_ORIGINS`: orígenes permitidos del frontend (p. ej. `http://localhost:5173`)
- `LAKEBASE_HOST`, `LAKEBASE_DBNAME` (y `LAKEBASE_PORT` si no es 5432)
- Validación JWT (según tu Entra App Registration/API):
  - `ENTRA_TENANT_ID`
  - `ENTRA_API_AUDIENCE`
  - `ENTRA_ISSUER`

> Nota: `DATABRICKS_SCOPE` ya viene definido por constitución; no cambiar salvo enmienda.

### Frontend (`frontend/.env`)

1. Copiar:
   - `frontend/.env.example` → `frontend/.env`
2. Completar como mínimo:

- `VITE_ENTRA_CLIENT_ID`
- `VITE_ENTRA_TENANT_ID`
- `VITE_ENTRA_AUTHORITY` (p. ej. `https://login.microsoftonline.com/<tenantId>`)
- `VITE_API_BASE_URL` (p. ej. `http://localhost:8000`)
- `VITE_API_SCOPES` (scope expuesto por tu API, p. ej. `api://<backend-app-id>/access_as_user`)

## Comandos (referencia)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

## Notas de seguridad

- NO commitear `backend/.env` ni `frontend/.env`.
- No imprimir tokens en logs (ni en frontend ni backend).
