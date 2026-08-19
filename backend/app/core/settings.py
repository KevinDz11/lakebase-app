from __future__ import annotations

import json
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Cargar siempre el .env correcto (backend/.env) aunque se ejecute uvicorn desde la raíz del repo
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        extra="ignore",
    )

    # App
    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Databricks SQL (Warehouse/Lakehouse Federation, usando databricks-sql-connector)
    DATABRICKS_SERVER_HOSTNAME: str = ""
    DATABRICKS_HTTP_PATH: str = ""
    DATABRICKS_TOKEN: str = ""

    # Lakebase (PostgreSQL) - deprecado para este MVP si usas Databricks SQL
    # Nota: en dev pueden venir vacíos; los endpoints fallarán con 500 hasta configurar backend/.env
    LAKEBASE_HOST: str = ""
    LAKEBASE_PORT: int = 5432
    LAKEBASE_DBNAME: str = ""
    LAKEBASE_SSLMODE: str = "require"

    # Entra token validation
    # Nota: en dev pueden venir vacíos; /api/* protegido regresará 401/500 hasta configurar backend/.env
    ENTRA_TENANT_ID: str = ""
    ENTRA_API_AUDIENCE: str = ""
    ENTRA_ISSUER: str = ""

    # Databricks scope (constante por constitución)
    DATABRICKS_SCOPE: str = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"

    def cors_origins_list(self) -> List[str]:
        """
        Acepta:
          - CSV: "http://localhost:5173,http://localhost:5174"
          - Con comillas: "\"http://localhost:5174\""
          - JSON list: ["http://localhost:5173","http://localhost:5174"]
        """
        raw = (self.CORS_ORIGINS or "").strip()
        if not raw:
            return []

        # JSON list
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(o).strip().strip("\"'") for o in parsed if str(o).strip()]
            except Exception:
                # fallback a CSV
                pass

        # CSV
        parts = raw.split(",")
        return [p.strip().strip("\"'") for p in parts if p.strip()]


settings = Settings()
