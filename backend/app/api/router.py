from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.filtros import router as filtros_router
from app.api.v1.health import router as health_router
from app.api.v1.kpis import router as kpis_router


api_router = APIRouter()
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(filtros_router, tags=["filtros"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(kpis_router, tags=["kpis"])
