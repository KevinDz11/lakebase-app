# Constitución del Proyecto: Explorador Lakebase con Azure Entra ID

## 1. Principios Fundamentales y Arquitectura

- **Estilo de Arquitectura**: Cliente-Servidor desacoplado (Frontend en React + Backend en FastAPI).
- **Cero Secretos Quemados**: Las contraseñas, secretos y cadenas de conexión NUNCA deben guardarse en el repositorio. Es obligatorio el uso de variables de entorno (`.env`) y tokens de Microsoft Entra ID.
- **Desarrollo Guiado por Especificaciones (Spec-Driven)**: Cada funcionalidad debe seguir el ciclo estricto: Especificación -> Plan Técnico -> Tareas de Implementación -> Código.

## 2. Estándares Tecnológicos

- **Backend**:
  - Python 3.11+ gestionado con `uv`.
  - Framework: FastAPI con validación mediante Pydantic v2.
  - Controlador de Base de Datos: `psycopg` (v3) para conectarse a Azure Databricks Lakebase usando el protocolo PostgreSQL.
  - Identidad de Azure: `azure-identity` mediante `DefaultAzureCredential` para adquirir tokens dinámicos de Entra ID.
- **Frontend**:
  - React 18+ con TypeScript (inicializado con Vite).
  - Estilos: Tailwind CSS.
  - Autenticación: Microsoft Authentication Library (`@azure/msal-react`, `@azure/msal-browser`).
  - Cliente HTTP: Axios o `fetch` nativo con interceptor para tokens Bearer.

## 3. Directrices de Seguridad y Entra ID

- La conexión a Lakebase DEBE usar un token OAuth2 dinámico con el scope de Azure Databricks (`2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default`) asignado como contraseña de PostgreSQL.
- Se deben aplicar políticas estrictas de CORS permitiendo únicamente el origen del frontend local y de producción.

## 4. Calidad de Código y Modularidad

- Estructura Backend: `backend/app/core` (configuración y autenticación), `backend/app/api` (rutas REST), `backend/app/services` (lógica de conexión y consultas a Lakebase).
- Estructura Frontend: `frontend/src/components`, `frontend/src/services`, `frontend/src/auth`, `frontend/src/pages`.
