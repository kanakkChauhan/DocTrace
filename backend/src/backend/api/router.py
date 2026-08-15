from fastapi import APIRouter

from backend.api.v1 import compliance, documents, health, trace

api_router = APIRouter()
api_router.include_router(health.router, prefix="/system")
api_router.include_router(documents.router, prefix="/documents")
api_router.include_router(trace.router, prefix="/trace")
api_router.include_router(compliance.router, prefix="/compliance")
