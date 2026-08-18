from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import psycopg

from backend.app.core.settings import settings


@dataclass(frozen=True)
class LakebaseConnInfo:
    host: str
    port: int
    dbname: str
    sslmode: str


def get_conn_info() -> LakebaseConnInfo:
    return LakebaseConnInfo(
        host=settings.LAKEBASE_HOST,
        port=settings.LAKEBASE_PORT,
        dbname=settings.LAKEBASE_DBNAME,
        sslmode=settings.LAKEBASE_SSLMODE,
    )


def _connect() -> psycopg.Connection[Any]:
    # Intencionalmente sin usuario/password: se espera que la autenticación sea
    # resuelta por la configuración local (p.ej. integraciones/secret store/etc).
    # Si tu Lakebase requiere user/pass, se agregan a Settings.
    info = get_conn_info()
    conn = psycopg.connect(
        host=info.host,
        port=info.port,
        dbname=info.dbname,
        sslmode=info.sslmode,
        connect_timeout=10,
    )
    return conn


def list_schemas() -> List[str]:
    sql = """
    select schema_name
    from information_schema.schemata
    where schema_name not in ('pg_catalog','information_schema')
    order by schema_name
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return [r[0] for r in cur.fetchall()]


def list_tables(schema: str) -> List[Tuple[str, str]]:
    sql = """
    select table_name, table_type
    from information_schema.tables
    where table_schema = %(schema)s
    order by table_name
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql, {"schema": schema})
        return [(r[0], r[1]) for r in cur.fetchall()]


def describe_table(schema: str, table: str) -> List[Dict[str, Any]]:
    sql = """
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
        cur.execute(sql, {"schema": schema, "table": table})
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
    sql = f'select * from "{schema}"."{table}" limit {limit}'
    with _connect() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute(sql)
        return list(cur.fetchall())
