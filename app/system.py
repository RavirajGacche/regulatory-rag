from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from shared.config import settings
from shared.constant import APP_VERSION

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str


class ReadyResponse(BaseModel):
    ready: bool
    checks: dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness: the process is running. No dependencies checked."""
    return HealthResponse(status="ok", environment=settings.environment, version=APP_VERSION)


@router.get("/ready", response_model=ReadyResponse)
async def ready(response: Response) -> ReadyResponse:
    """Readiness: dependencies are reachable. Real checks arrive in Phase 2."""
    checks = {"postgres": "not_wired", "redis": "not_wired"}
    ok = all(v in ("ok", "not_wired") for v in checks.values())
    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadyResponse(ready=ok, checks=checks)
