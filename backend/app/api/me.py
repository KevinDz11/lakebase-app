from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends

from backend.app.core.auth import get_current_claims

router = APIRouter(prefix="/api", tags=["auth"])


@router.get("/me")
def me(claims: Dict[str, Any] = Depends(get_current_claims)):
    # No devolvemos el token; solo claims útiles.
    allowed = ["sub", "oid", "tid", "upn", "preferred_username", "name", "aud", "iss", "scp", "roles"]
    return {k: claims.get(k) for k in allowed if k in claims}
