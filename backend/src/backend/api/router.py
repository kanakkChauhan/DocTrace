from fastapi import APIRouter

from src.backend.api.v1 import documents, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/system")
api_router.include_router(documents.router, prefix="/documents")
