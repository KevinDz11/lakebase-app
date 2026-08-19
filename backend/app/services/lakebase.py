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


def list_schemas() -> List[str]:
    sql_text = """
    select schema_name
    from information_schema.schemata
    where schema_name not in ('pg_catalog','information_schema')
    order by schema_name
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql_text)
        return [r[0] for r in cur.fetchall()]


def list_tables(schema: str) -> List[Tuple[str, str]]:
    sql_text = """
    select table_name, table_type
    from information_schema.tables
    where table_schema = %(schema)s
    order by table_name
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql_text, {"schema": schema})
        return [(r[0], r[1]) for r in cur.fetchall()]


def describe_table(schema: str, table: str) -> List[Dict[str, Any]]:
    sql_text = """
    select
      column_name,
      data_type,
      is_nullable,
      ordinal_position
    from information_schema.columns
    where table_schema = %(schema)s and table_name = %(table)s
    order by ordinal_position
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql_text, {"schema": schema, "table": table})
        rows = cur.fetchall()
        return [
            {
                "column_name": r[0],
                "data_type": r[1],
                "is_nullable": r[2],
                "ordinal_position": r[3],
            }
            for r in rows
        ]


def preview_rows(schema: str, table: str, limit: int = 20) -> List[Dict[str, Any]]:
    limit = max(1, min(int(limit), 200))
    sql_text = f'SELECT * FROM "{schema}"."{table}" LIMIT {limit}'
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql_text)
        cols = [d[0] for d in cur.description] if cur.description else []
        return [dict(zip(cols, row)) for row in cur.fetchall()]
