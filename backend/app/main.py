from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.explorer import router as explorer_router
from backend.app.api.me import router as me_router
from backend.app.core.settings import settings

app = FastAPI(title="Lakebase Entra ID Explorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(me_router)
app.include_router(explorer_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
