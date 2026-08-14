from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthCheck(BaseModel):
    status: str
    environment: str
    version: str


@router.get("/health", response_model=HealthCheck, tags=["System"])
async def health_check() -> HealthCheck:
    from backend.core.config import settings

    return HealthCheck(status="ok", environment=settings.ENVIRONMENT, version="0.1.0")
