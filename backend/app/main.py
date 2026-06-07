"""HandwritOCR FastAPI Application.

Main entry point for the backend server.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router
from app.api.websocket import router as ws_router

# ─── Logging ───────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ─── FastAPI App ───────────────────────────────────────
app = FastAPI(
    title="HandwritOCR API",
    description="Handwriting synthesis backend — transform text into realistic handwriting",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS Middleware ───────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ────────────────────────────────────────────
app.include_router(api_router)
app.include_router(ws_router)


# ─── Startup / Shutdown ───────────────────────────────
@app.on_event("startup")
async def startup_event() -> None:
    """Ensure storage directories exist on startup."""
    logger.info("HandwritOCR API starting up...")
    logger.info(f"Storage: {settings.storage_dir}")
    logger.info(f"CORS origins: {settings.cors_origin_list}")
    # Ensure dirs exist
    _ = settings.upload_dir
    _ = settings.output_dir
    logger.info("HandwritOCR API ready.")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("HandwritOCR API shutting down...")


# ─── Root Redirect ─────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "app": "HandwritOCR API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }
