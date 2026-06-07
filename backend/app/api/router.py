"""Main API router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints import health, samples, generate, download

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(samples.router)
api_router.include_router(generate.router)
api_router.include_router(download.router)
