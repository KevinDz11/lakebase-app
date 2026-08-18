from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.core.auth import get_current_claims
from backend.app.services import lakebase

router = APIRouter(prefix="/api/explorer", tags=["explorer"])


@router.get("/schemas", response_model=List[str])
def get_schemas(_: Dict[str, Any] = Depends(get_current_claims)) -> List[str]:
    try:
        return lakebase.list_schemas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lakebase error: {type(e).__name__}")


@router.get("/schemas/{schema}/tables")
def get_tables(
    schema: str,
    _: Dict[str, Any] = Depends(get_current_claims),
):
    try:
        tables = lakebase.list_tables(schema)
        return [{"table_name": t[0], "table_type": t[1]} for t in tables]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lakebase error: {type(e).__name__}")


@router.get("/schemas/{schema}/tables/{table}/describe", response_model=List[Dict[str, Any]])
def describe(
    schema: str,
    table: str,
    _: Dict[str, Any] = Depends(get_current_claims),
) -> List[Dict[str, Any]]:
    try:
        return lakebase.describe_table(schema, table)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lakebase error: {type(e).__name__}")


@router.get("/schemas/{schema}/tables/{table}/preview", response_model=List[Dict[str, Any]])
def preview(
    schema: str,
    table: str,
    limit: int = Query(default=20, ge=1, le=200),
    _: Dict[str, Any] = Depends(get_current_claims),
) -> List[Dict[str, Any]]:
    try:
        return lakebase.preview_rows(schema, table, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lakebase error: {type(e).__name__}")
