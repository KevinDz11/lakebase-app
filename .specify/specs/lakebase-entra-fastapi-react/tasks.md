# Tareas: Conexión FastAPI ↔ Azure Databricks Lakebase con Microsoft Entra ID + Frontend React

**Input**: Documentos de diseño en `.specify/specs/lakebase-entra-fastapi-react/` y spec en `.specify/specs/feature-spec-lakebase-entra-fastapi-react-es.md`

**Prerequisites**: plan.md (requerido), spec (requerido)

**Tests**: No se incluyen tareas de pruebas automatizadas porque la especificación no las solicitó explícitamente (se puede añadir una fase de tests si se requiere).

**Organización**: Tareas agrupadas por historias de usuario (US1, US2, US3) para permitir implementación y validación incremental.

## Formato: `[ID] [P?] [US?] Descripción`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias directas)
- **[US]**: historia de usuario objetivo (US1/US2/US3)
- Se incluyen rutas de archivos previstas según el plan (a crear si no existen)

---

## Phase 1: Setup (Infraestructura compartida)

- [ ] T001 Crear estructura base de carpetas para la app web:
  - `backend/app/{core,api,services}`
  - `frontend/src/{auth,components,services,pages}`
- [ ] T002 Inicializar Backend FastAPI (Python 3.11+) gestionado con `uv` en `backend/` e instalar dependencias:
  - `fastapi`, `uvicorn`, `pydantic` v2, `azure-identity`, `psycopg` v3
- [ ] T003 Inicializar Frontend React (Vite + TS) en `frontend/` e instalar dependencias:
  - `react`, `@azure/msal-react`, `@azure/msal-browser`
- [ ] T004 [P] Crear archivos base de configuración de entorno (sin secretos):
  - `backend/.env.example` (solo nombres de variables)
  - `frontend/.env.example` (solo nombres de variables)
- [ ] T005 [P] Documentar variables de entorno requeridas en `README` o `.specify/specs/lakebase-entra-fastapi-react/quickstart.md` (si existe) incluyendo:
  - orígenes CORS permitidos
  - host/puerto/dbname Lakebase
  - MSAL clientId/tenant/authority

---

## Phase 2: Foundational (Bloqueante)

**⚠️ CRITICAL**: No iniciar tareas de historias de usuario hasta completar esta fase.

- [ ] T006 Implementar configuración central del backend en `backend/app/core/config.py` (Pydantic Settings):
  - CORS origins
  - Lakebase host/port/dbname/sslmode
  - parámetros de validación JWT (audience/tenant/issuer según decisión)
- [ ] T007 Implementar CORS estricto en `backend/app/main.py` leyendo de `config.py`
- [ ] T008 Implementar base de logging sin secretos en `backend/app/core/logging.py`
- [ ] T009 Implementar autenticación/autorizar requests (validación JWT) en `backend/app/core/auth.py` y dependencia en `backend/app/api/deps.py`
- [ ] T010 Implementar adquisición/caché de token Databricks en `backend/app/services/databricks_tokens.py` usando:
  - `DefaultAzureCredential`
  - scope `2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default`
- [ ] T011 Implementar cliente Lakebase en `backend/app/services/lakebase.py` usando `psycopg`:
  - construir conexión usando token Databricks como password
  - timeout y manejo de error estandarizado
  - helper `run_select_one()` (o equivalente) para query segura

**Checkpoint**: Foundation lista — se puede iniciar US1/US2/US3.

---

## Phase 3: User Story 1 (P1) — Login + Estado de conexión (MVP)

**Meta**: Usuario inicia sesión en React y puede verificar conectividad a Lakebase vía backend.

**Prueba independiente**: UI muestra login, obtiene token, llama `/api/health/lakebase` y renderiza “Conectado” o error.

### Backend (US1)

- [ ] T012 [US1] Crear router de health en `backend/app/api/health.py`:
  - `GET /api/health/lakebase`
  - requiere auth (dep de `get_current_user`)
  - verifica token Databricks + conexión Lakebase (sin exponer secretos)
- [ ] T013 [US1] Registrar router en `backend/app/main.py` (prefijo `/api`)
- [ ] T014 [US1] Normalizar errores y respuestas (401/403/500) para que el frontend muestre mensajes accionables

### Frontend (US1)

- [ ] T015 [US1] Configurar MSAL en `frontend/src/auth/msalConfig.ts` (valores via env)
- [ ] T016 [US1] Implementar provider/wrapper en `frontend/src/auth/msalProvider.tsx` e integrarlo en `frontend/src/main.tsx`
- [ ] T017 [US1] Implementar helper de token en `frontend/src/auth/token.ts`:
  - `acquireTokenSilent` (y fallback interactivo)
- [ ] T018 [US1] Implementar cliente API con interceptor Bearer en `frontend/src/services/apiClient.ts`
- [ ] T019 [US1] Implementar llamada `health()` en `frontend/src/services/lakebaseApi.ts`
- [ ] T020 [US1] Implementar componente `ConnectionStatus` en `frontend/src/components/ConnectionStatus.tsx`:
  - botón “Probar conexión”
  - estados loading/success/error
- [ ] T021 [US1] Integrar `ConnectionStatus` en `frontend/src/pages/Home.tsx`

**Checkpoint**: MVP de US1 funcional.

---

## Phase 4: User Story 2 (P2) — Consulta de ejemplo `SELECT 1`

**Meta**: Usuario ejecuta una consulta segura de ejemplo desde UI y ve el resultado.

**Prueba independiente**: Desde la UI, ejecutar “Consulta de ejemplo” y ver `{ rows: [[1]] }`.

### Backend (US2)

- [ ] T022 [US2] Implementar endpoint en `backend/app/api/query.py`:
  - `POST /api/query/example`
  - requiere auth
  - ejecuta `SELECT 1` vía `lakebase.py`
  - retorna columnas/filas/elapsedMs
- [ ] T023 [US2] Agregar validaciones y manejo de error para fallos de token/conexión

### Frontend (US2)

- [ ] T024 [US2] Agregar método `queryExample()` en `frontend/src/services/lakebaseApi.ts`
- [ ] T025 [US2] Crear componente `QueryExample` en `frontend/src/components/QueryExample.tsx`
- [ ] T026 [US2] Integrar `QueryExample` en `frontend/src/pages/Home.tsx`

**Checkpoint**: US2 funcional sin romper US1.

---

## Phase 5: User Story 3 (P3) — Listado mínimo de metadata (schemas)

**Meta**: Usuario lista schemas (o subset) desde Lakebase con paginación simple.

**Prueba independiente**: UI muestra lista de schemas con “siguiente página” si aplica.

### Backend (US3)

- [ ] T027 [US3] Implementar endpoint en `backend/app/api/metadata.py`:
  - `GET /api/metadata/schemas?page=&pageSize=`
  - requiere auth
  - ejecuta consulta predefinida (sin SQL arbitrario)
  - retorna items + nextPage si aplica
- [ ] T028 [US3] Definir límites por defecto (pageSize máximo) y validación de parámetros

### Frontend (US3)

- [ ] T029 [US3] Agregar método `listSchemas(page, pageSize)` en `frontend/src/services/lakebaseApi.ts`
- [ ] T030 [US3] Crear UI simple (componente o sección en `Home.tsx`) para mostrar schemas y paginar

**Checkpoint**: US3 funcional.

---

## Phase 6: Pulido y preocupaciones transversales

- [ ] T031 [P] Revisar que no haya secretos en repo:
  - asegurar `.env` real esté en `.gitignore`
  - validar que `.env.example` no contenga valores sensibles
- [ ] T032 Mejorar mensajes de error en frontend (mapear 401/403/500 a copy claro)
- [ ] T033 Añadir documentación de ejecución local (backend + frontend) y troubleshooting (credenciales `DefaultAzureCredential`, CORS, permisos Lakebase)
- [ ] T034 Revisión de seguridad mínima:
  - no loguear tokens
  - limitar endpoints a consultas controladas
  - verificar CORS

---

## Dependencies & Execution Order (resumen)

- Phase 1 → Phase 2 (bloqueante) → US1 (MVP) → US2 → US3 → Pulido
- Tareas marcadas [P] pueden ejecutarse en paralelo si hay capacidad, evitando colisiones de archivos.
