from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from databricks import sql

from backend.app.core.settings import settings


@dataclass(frozen=True)
class DatabricksSqlConnInfo:
    server_hostname: str
    http_path: str
    token: str


def get_conn_info() -> DatabricksSqlConnInfo:
    return DatabricksSqlConnInfo(
        server_hostname=settings.DATABRICKS_SERVER_HOSTNAME,
        http_path=settings.DATABRICKS_HTTP_PATH,
        token=settings.DATABRICKS_TOKEN,
    )


def _connect() -> sql.Connection:
    info = get_conn_info()
    if not info.server_hostname or not info.http_path or not info.token:
        raise RuntimeError(
            "Missing Databricks SQL connection settings. Set "
            "DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN in backend/.env"
        )

    return sql.connect(
        server_hostname=info.server_hostname,
        http_path=info.http_path,
        access_token=info.token,
    )


def list_catalogs() -> List[str]:
    with _connect() as conn, conn.cursor() as cur:
        cur.execute("SHOW CATALOGS")
        return [r[0] for r in cur.fetchall()]


def list_schemas(catalog: str) -> List[str]:
    # En Databricks SQL, SHOW SCHEMAS no acepta quotes en el nombre del catálogo.
    # Ejemplo válido: SHOW SCHEMAS IN samples
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(f"SHOW SCHEMAS IN {catalog}")
        return [r[0] for r in cur.fetchall()]


def list_tables(catalog: str, schema: str) -> List[Tuple[str, str]]:
    with _connect() as conn, conn.cursor() as cur:
        # Igual: sin quotes.
        cur.execute(f"SHOW TABLES IN {catalog}.{schema}")
        rows = cur.fetchall()
        out: List[Tuple[str, str]] = []
        for r in rows:
            table_name = r[1] if len(r) > 1 else r[0]
            out.append((table_name, "TABLE"))
        return out


def describe_table(catalog: str, schema: str, table: str) -> List[Dict[str, Any]]:
    # Evitar information_schema y quotes; usar DESCRIBE TABLE en Unity Catalog
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(f"DESCRIBE TABLE {catalog}.{schema}.{table}")
        rows = cur.fetchall()

        # Databricks devuelve columnas tipo: col_name, data_type, comment
        # y luego secciones (# Partition Information, etc). Filtramos.
        out: List[Dict[str, Any]] = []
        pos = 1
        for r in rows:
            col_name = (r[0] or "").strip() if len(r) > 0 else ""
            data_type = (r[1] or "").strip() if len(r) > 1 else ""
            if not col_name or col_name.startswith("#"):
                continue
            if col_name.lower() in ("partition", "col_name"):
                continue
            out.append(
                {
                    "column_name": col_name,
                    "data_type": data_type,
                    "is_nullable": "",
                    "ordinal_position": pos,
                }
            )
            pos += 1
        return out


def preview_rows(
    catalog: str, schema: str, table: str, limit: int = 20
) -> List[Dict[str, Any]]:
    limit = max(1, min(int(limit), 200))
    sql_text = f"SELECT * FROM {catalog}.{schema}.{table} LIMIT {limit}"
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql_text)
        cols = [d[0] for d in cur.description] if cur.description else []
        return [dict(zip(cols, row)) for row in cur.fetchall()]
