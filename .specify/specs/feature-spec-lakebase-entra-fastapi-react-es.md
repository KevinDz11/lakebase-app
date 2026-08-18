# Especificación de Funcionalidad: Conexión FastAPI ↔ Azure Databricks Lakebase con Microsoft Entra ID + Frontend React

**Rama de feature**: `[###-lakebase-entra-fastapi-react]`

**Creado**: 2026-08-18

**Estado**: Borrador

**Input**: User description: "Crea la especificación en español para conectar FastAPI con Azure Databricks Lakebase usando Microsoft Entra ID y un frontend en React"

## Escenarios de usuario y pruebas _(obligatorio)_

### Historia de Usuario 1 - Iniciar sesión y ver estado de conexión (Priority: P1)

Como usuario, quiero iniciar sesión con Microsoft Entra ID en el frontend y ver si el backend puede conectarse a Lakebase, para confirmar que mi sesión y permisos son correctos.

**Por qué esta prioridad**: Es el “happy path” mínimo para validar autenticación end-to-end y acceso a Lakebase sin exponer secretos.

**Prueba independiente**: Puede probarse ejecutando el frontend, iniciando sesión, y llamando un endpoint de “health/connection” que confirme obtención de token de Databricks y conexión a Lakebase.

**Escenarios de aceptación**:

1. **Dado** que el usuario no ha iniciado sesión, **Cuando** abre la app, **Entonces** se le solicita autenticarse con Entra ID.
2. **Dado** que el usuario inició sesión correctamente, **Cuando** presiona “Probar conexión”, **Entonces** ve un resultado “Conectado” y metadatos básicos (p. ej., timestamp, tenant) sin secretos.
3. **Dado** que el token no tiene permisos para Lakebase, **Cuando** presiona “Probar conexión”, **Entonces** ve un error manejado con mensaje accionable (sin detalles sensibles).

---

### Historia de Usuario 2 - Ejecutar una consulta de ejemplo desde la UI (Priority: P2)

Como usuario autenticado, quiero ejecutar una consulta de ejemplo (p. ej., `SELECT 1`) contra Lakebase desde el frontend, para validar que el flujo de tokens funciona para consultas reales.

**Por qué esta prioridad**: Valida que no solo existe conexión, sino que el backend puede ejecutar SQL con el token OAuth2 como “password” y retornar resultados.

**Prueba independiente**: Llamar a un endpoint `/api/query` con un payload controlado (consulta permitida) y verificar respuesta en UI.

**Escenarios de aceptación**:

1. **Dado** que el usuario está autenticado, **Cuando** ejecuta la consulta de ejemplo, **Entonces** la UI muestra el resultado y la latencia aproximada.
2. **Dado** que el backend falla al obtener token de Databricks, **Cuando** se ejecuta la consulta, **Entonces** retorna un error 401/403/500 clasificado y entendible para usuario.

---

### Historia de Usuario 3 - Listar objetos/metadata mínimo (Priority: P3)

Como usuario autenticado, quiero listar un conjunto mínimo de metadata (p. ej., bases de datos/esquemas) desde Lakebase para explorar el entorno.

**Por qué esta prioridad**: Aporta valor exploratorio y prueba endpoints de lectura más realistas.

**Prueba independiente**: Endpoint `/api/metadata/schemas` que retorna lista paginada.

**Escenarios de aceptación**:

1. **Dado** que el usuario está autenticado, **Cuando** navega a “Explorar”, **Entonces** ve una lista de schemas (o un mensaje de “sin acceso” si aplica).
2. **Dado** que la lista es grande, **Cuando** solicita la siguiente página, **Entonces** el backend retorna datos paginados.

---

### Casos borde

- ¿Qué pasa cuando el frontend corre desde un origen no permitido por CORS?
- ¿Qué pasa cuando `DefaultAzureCredential` no encuentra credenciales en el entorno (local/CI)?
- ¿Qué pasa cuando el token de Entra expira en el frontend (MSAL) o el token de Databricks expira en el backend durante una consulta?
- ¿Cómo se maneja un error de red/transitorio con Lakebase (retry/backoff)?
- ¿Cómo se evita que el usuario ejecute SQL arbitrario (inyección/abuso)?

## Requerimientos _(obligatorio)_

### Requerimientos funcionales

- **FR-001**: El frontend **DEBE** autenticar usuarios con MSAL (`@azure/msal-react`, `@azure/msal-browser`) contra Microsoft Entra ID.
- **FR-002**: El frontend **DEBE** adjuntar el access token de Entra ID como Bearer token en llamadas al backend (interceptor en Axios o wrapper de `fetch`).
- **FR-003**: El backend (FastAPI) **DEBE** validar el Bearer token entrante (JWT) para autorizar acceso a endpoints protegidos.
- **FR-004**: El backend **NO DEBE** contener secretos hardcodeados (cumple “Zero Hardcoded Secrets”).
- **FR-005**: El backend **DEBE** obtener un token OAuth2 para Azure Databricks usando `azure-identity` (`DefaultAzureCredential`) con el scope: `2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default`.
- **FR-006**: El backend **DEBE** usar el token de Databricks obtenido como “password” al conectarse a Lakebase vía `psycopg` (PostgreSQL wire-protocol).
- **FR-007**: El backend **DEBE** exponer un endpoint de verificación de conectividad (p. ej. `/api/health/lakebase`) que confirme conectividad sin revelar secretos.
- **FR-008**: El backend **DEBE** exponer un endpoint para consulta controlada (p. ej. `/api/query/example`) que ejecute una consulta segura (por defecto `SELECT 1`) y retorne resultado.
- **FR-009**: El backend **DEBE** implementar CORS estricto para permitir solo orígenes configurados del frontend.
- **FR-010**: El frontend **DEBE** mostrar mensajes de error accionables (p. ej., “Sin permisos”, “Credenciales no encontradas”, “Origen no permitido”) sin filtrar detalles sensibles.

### Entidades clave _(si involucra datos)_

- **Sesión de Usuario**: contexto autenticado del usuario en el frontend (cuenta, tenant, expiración).
- **LakebaseConnectionConfig**: host/puerto/dbname/sslmode + configuración de token (sin secretos persistidos).
- **QueryRequest**: consulta permitida/operación (en v1: solo consulta de ejemplo o lista controlada).
- **QueryResult**: filas/columnas + metadata (latencia, timestamp) sin información sensible.

## Criterios de éxito _(obligatorio)_

### Resultados medibles

- **SC-001**: Un usuario puede iniciar sesión y ver estado “Conectado” (health) en menos de 60s en un entorno configurado.
- **SC-002**: La consulta de ejemplo retorna un resultado correcto (p. ej., `1`) con latencia p50 < 2s en red normal.
- **SC-003**: En escenarios sin permisos/token inválido, el sistema retorna errores clasificados (401/403) sin exponer tokens ni strings de conexión.
- **SC-004**: No existen secretos hardcodeados en el repositorio (verificado por revisión/escaneo simple).

## Suposiciones

- El equipo tiene un App Registration en Entra ID para el frontend y/o backend (o configuración equivalente) y conoce sus valores (clientId/tenantId) vía variables de entorno.
- El entorno (local/CI) tiene una forma soportada para que `DefaultAzureCredential` obtenga credenciales (Azure CLI login, Managed Identity, VS Code/Azure Account, etc.).
- Lakebase está accesible desde la red donde corre el backend (firewall/peering resuelto).
- Para v1, la ejecución de SQL estará restringida (sin SQL arbitrario desde UI).
- Las URLs permitidas por CORS serán provistas por configuración (no hardcodeadas).
