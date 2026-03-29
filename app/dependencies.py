from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

_bearer = HTTPBearer()


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(_bearer)],
) -> int:
    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{settings.auth_service_url}/api/v1/introspect",
                json={"token": token},
                headers={"x-service-key": settings.auth_service_introspect_key},
                timeout=5.0,
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth service unavailable",
            )

    data = resp.json()
    if not data.get("active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return int(data["sub"])
