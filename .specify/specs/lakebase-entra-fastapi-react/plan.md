# Plan de Implementación: Conexión FastAPI ↔ Azure Databricks Lakebase con Microsoft Entra ID + Frontend React

**Branch**: `[###-lakebase-entra-fastapi-react]` | **Date**: 2026-08-18 | **Spec**: `../feature-spec-lakebase-entra-fastapi-react-es.md`

**Input**: Feature specification en `.specify/specs/feature-spec-lakebase-entra-fastapi-react-es.md`

**Nota**: Este documento es la salida del flujo `/speckit.plan` y describe la arquitectura, estructura de código y decisiones técnicas para implementar la especificación.

## Summary

Se implementará una aplicación web desacoplada con **Frontend React (Vite + TS + Tailwind)** y **Backend FastAPI (Python 3.11+)** que:

1. Autentique al usuario con **Microsoft Entra ID** desde el cliente (MSAL).
2. Use el token del usuario para autorizar llamadas al backend (JWT Bearer).
3. En el backend, adquiera un token OAuth2 de **Azure Databricks** mediante `DefaultAzureCredential` con scope `2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default`.
4. Conecte a **Lakebase** vía `psycopg` usando ese token como “password” y ejecute endpoints controlados (`health`, `SELECT 1`, metadata).

## Technical Context

**Lenguaje/Versión**:

- Backend: Python 3.11+
- Frontend: Node 18+ / React 18+ / TypeScript

**Dependencias primarias**:

- Backend: FastAPI, Pydantic v2, `azure-identity`, `psycopg` v3
- Frontend: React, Vite, Tailwind, `@azure/msal-react`, `@azure/msal-browser`

**Storage**: Lakebase (PostgreSQL wire-protocol a través de Azure Databricks)

**Testing**:

- Backend: pytest (unit + integración), httpx TestClient
- Frontend: Vitest/React Testing Library (opcional en fase inicial)

**Plataforma objetivo**: Web + backend HTTP (Linux/Windows en dev; despliegue en contenedor o App Service)

**Tipo de proyecto**: Web application (frontend + backend)

**Metas de performance**:

- p50 < 2s para consulta de ejemplo en entorno normal (según spec)
- p95 razonable (<5s) sin retries agresivos

**Restricciones**:

- Cero secretos hardcodeados (constitución)
- CORS estricto
- No permitir SQL arbitrario en v1

**Escala/alcance**: MVP funcional para validar end-to-end auth + conectividad + consulta simple

## Constitution Check

_GATE: Debe pasar antes de diseño detallado/implementación._

Checklist basado en `.specify/memory/constitution.md`:

- [x] Arquitectura desacoplada: frontend React + backend FastAPI.
- [x] Cero secretos hardcodeados: config solo por variables de entorno.
- [x] Spec‑Driven: esta planificación deriva de la especificación.
- [x] Tech stack: FastAPI/Pydantic v2, `uv`, `psycopg` v3, `azure-identity`, MSAL React.
- [x] Token Databricks: scope `2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default`.

## Project Structure

### Documentación (esta feature)

```text
.specify/specs/lakebase-entra-fastapi-react/
├── plan.md              # Este archivo (/speckit.plan)
└── (futuros)
    ├── research.md
    ├── data-model.md
    ├── quickstart.md
    ├── contracts/
    └── tasks.md          # /speckit.tasks
```

> Nota: La especificación actual está en `.specify/specs/feature-spec-lakebase-entra-fastapi-react-es.md`.
> Si se desea alinear 100% al template (carpeta por feature), se puede mover/duplicar la spec a:
> `.specify/specs/lakebase-entra-fastapi-react/spec.md` en una iteración posterior.

### Código fuente (raíz del repo)

```text
# Aplicación web (frontend + backend)

backend/
├── app/
│   ├── core/
│   │   ├── config.py              # variables de entorno, settings Pydantic
│   │   ├── auth.py                # validación JWT (Entra) para requests entrantes
│   │   └── logging.py             # logging estructurado (sin secretos)
│   ├── services/
│   │   ├── databricks_tokens.py   # adquisición/caché de token Databricks (DefaultAzureCredential)
│   │   └── lakebase.py            # conexión psycopg + helpers de query/metadata
│   ├── api/
│   │   ├── deps.py                # dependencias: auth, settings, service inject
│   │   ├── health.py              # /api/health/lakebase
│   │   ├── query.py               # /api/query/example
│   │   └── metadata.py            # /api/metadata/...
│   └── main.py                    # FastAPI app + routers + CORS
└── tests/
    ├── unit/
    └── integration/

frontend/
├── src/
│   ├── auth/
│   │   ├── msalConfig.ts          # config MSAL (clientId/authority/redirectUri)
│   │   ├── msalProvider.tsx       # wrapper para MsalProvider + login UI helpers
│   │   └── token.ts               # helper para adquirir token (acquireTokenSilent)
│   ├── services/
│   │   ├── apiClient.ts           # fetch/axios wrapper con interceptor Bearer
│   │   └── lakebaseApi.ts         # funciones: health(), queryExample(), listSchemas()
│   ├── components/
│   │   ├── ConnectionStatus.tsx   # UI de estado y botón “Probar conexión”
│   │   └── QueryExample.tsx       # UI para ejecutar SELECT 1
│   └── pages/
│       └── Home.tsx
└── (vite config, tailwind config, etc.)
```

**Decisión de estructura**:

- Se adopta el layout “Web application” del template.
- El backend se organiza estrictamente en `app/core`, `app/services`, `app/api` como define la constitución.
- El frontend se organiza en `src/auth`, `src/components`, `src/services` (y `src/pages` para navegación mínima).

## Flujo de autenticación y tokens (detallado)

### A) Cliente (React) — MSAL + Bearer hacia FastAPI

1. **Inicialización MSAL**
   - `msalConfig.ts` define:
     - `clientId` (App Registration)
     - `authority` (tenant o common/organizations según política)
     - `redirectUri`
     - `cacheLocation` (session/local storage según preferencia)
   - Se envuelve la app con `MsalProvider`.

2. **Login**
   - UI dispara `loginRedirect()` o `loginPopup()`.
   - Se obtiene `account` activa.

3. **Adquisición de token para API**
   - Antes de llamar al backend:
     - `acquireTokenSilent({ scopes: [...] , account })`
   - Scopes:
     - Idealmente un scope de API propio (exponer un scope en Entra para el backend).
     - Si aún no existe, se documenta como dependencia/decisión pendiente.

4. **Llamada al backend**
   - `apiClient.ts` agrega header:
     - `Authorization: Bearer <access_token>`
   - Si falla `acquireTokenSilent`, se cae a interacción (redirect/popup).

5. **Renovación**
   - MSAL gestiona refresh/renovación; el cliente solo reintenta obtener token silencioso.

### B) Backend (FastAPI) — Validación JWT entrante

1. Middleware/dependency en `app/core/auth.py`:
   - Extrae Bearer token de `Authorization`.
   - Valida firma y claims:
     - `iss`, `aud`, `exp`, `tid` (según política)
   - Rechaza con 401/403 cuando corresponda.
   - No loguea tokens.

2. `app/api/deps.py` expone `get_current_user()` para routers.

### C) Backend — Token de Databricks con DefaultAzureCredential

1. En `app/services/databricks_tokens.py`:
   - Instancia `DefaultAzureCredential()`.
   - Solicita token con:
     - scope: `2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default`
   - Implementa caché in-memory por `expires_on` para evitar pedir token en cada request.

2. Manejo de errores:
   - Si no hay credenciales en entorno: error claro y controlado.
   - Si el scope no es válido o no hay permisos: mapear a 403/500 según caso.

### D) Backend — Conexión a Lakebase con psycopg v3

1. `app/services/lakebase.py`:
   - Obtiene token Databricks (sección C).
   - Construye conexión a PostgreSQL (Lakebase):
     - host/port/dbname/sslmode desde variables de entorno
     - **password = access token** (string)
   - Usa `psycopg.connect(...)` con SSL requerido (según Lakebase).

2. Ejecución de consultas:
   - Para v1:
     - endpoint `queryExample()` ejecuta `SELECT 1`.
   - En próximos incrementos:
     - metadata endpoints con queries predefinidas.
   - No permitir SQL arbitrario proveniente del cliente en v1.

3. Consideraciones:
   - Reusar conexión/pool: opcional; inicial: conexión por request con timeout.
   - Timeouts y retries moderados para errores transitorios.

## API Contracts (alto nivel)

- `GET /api/health/lakebase`
  - 200: `{ status: "connected" | "error", timestamp, details?: ... }`
- `POST /api/query/example`
  - 200: `{ columns, rows, elapsedMs }`
- `GET /api/metadata/schemas?page=&pageSize=`
  - 200: `{ items: [...], nextPage?: ... }`

## Riesgos y mitigaciones

- **Riesgo**: Validación JWT compleja (keys rota/rotación).
  - Mitigación: usar librería robusta (p. ej. `python-jose`/`PyJWT` + jwks cache) y tests.
- **Riesgo**: Config de scopes/audience incorrectos entre frontend y backend.
  - Mitigación: documentar en quickstart + validar `aud` explícitamente.
- **Riesgo**: Exposición accidental de secretos en logs.
  - Mitigación: sanitización + reglas explícitas de logging.

## Complejidad (si aplica)

| Violación | Por qué se necesita | Alternativa más simple rechazada porque |
| --------- | ------------------- | --------------------------------------- |
| N/A       | N/A                 | N/A                                     |
