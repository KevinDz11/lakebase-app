from __future__ import annotations
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Lakebase (PostgreSQL)
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
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
