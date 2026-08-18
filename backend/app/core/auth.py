from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from backend.app.core.settings import settings

bearer_scheme = HTTPBearer(auto_error=False)

_jwks_cache: Optional[Dict[str, Any]] = None


def _jwks_url() -> str:
    # v2.0 issuer typically: https://login.microsoftonline.com/<tenantId>/v2.0
    return f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}/discovery/v2.0/keys"


def _get_jwks() -> Dict[str, Any]:
    global _jwks_cache
    if _jwks_cache is None:
        resp = requests.get(_jwks_url(), timeout=10)
        resp.raise_for_status()
        _jwks_cache = resp.json()
    return _jwks_cache


def _get_signing_key(kid: str) -> Dict[str, Any]:
    jwks = _get_jwks()
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            return k
    raise HTTPException(status_code=401, detail="Signing key not found")


def get_current_claims(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Dict[str, Any]:
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = creds.credentials

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Invalid token header")

        key = _get_signing_key(kid)
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.ENTRA_API_AUDIENCE,
            issuer=settings.ENTRA_ISSUER,
            options={"verify_at_hash": False},
        )
        return claims
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
