from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.explorer import router as explorer_router
from backend.app.api.me import router as me_router
from backend.app.core.settings import settings

app = FastAPI(title="Lakebase Entra ID Explorer API")

# CORS dev fallback (cuando el middleware estándar no está agregando allow-origin)
_DEV_ALLOWED_ORIGINS = {"http://localhost:5173", "http://localhost:5174"}


@app.middleware("http")
async def _dev_cors_fallback(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method == "OPTIONS":
        print(f"[cors] OPTIONS origin={origin!r} acrh={request.headers.get('access-control-request-headers')!r}")
    # Manejo explícito de preflight
    origin_ok = False
    if origin:
        origin_ok = (origin in _DEV_ALLOWED_ORIGINS) or ("localhost:5173" in origin) or ("localhost:5174" in origin)

    if request.method == "OPTIONS" and origin_ok:
        resp = Response(status_code=200)
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = request.headers.get(
            "access-control-request-headers",
            "*",
        )
        return resp

    response = await call_next(request)
    if origin_ok:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.on_event("startup")
def _log_settings_on_startup():
    # Ayuda a depurar CORS/env. No imprime secretos.
    print(f"[startup] module_file={__file__}")
    print(f"[startup] APP_ENV={settings.APP_ENV}")
    print(f"[startup] CORS_ORIGINS(raw)={settings.CORS_ORIGINS!r}")
    print(f"[startup] CORS_ORIGINS(list)={settings.cors_origins_list()}")


# Nota: CORSMiddleware deshabilitado porque en este entorno está rechazando preflight
# con "Disallowed CORS origin". Usamos el middleware _dev_cors_fallback de arriba.

app.include_router(me_router)
app.include_router(explorer_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
