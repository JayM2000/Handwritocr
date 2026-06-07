"""Health check endpoint."""

from fastapi import APIRouter
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check() -> HealthResponse:
    """Check the health of the API and its dependencies."""
    redis_ok = False
    celery_ok = False

    # Check Redis
    try:
        import redis as redis_lib
        from app.config import settings

        r = redis_lib.from_url(settings.redis_url, socket_timeout=2)
        r.ping()
        redis_ok = True
    except Exception:
        pass

    # Check Celery
    try:
        from app.tasks.celery_app import celery_app

        insp = celery_app.control.inspect(timeout=2)
        if insp.ping():
            celery_ok = True
    except Exception:
        pass

    return HealthResponse(
        status="ok",
        redis=redis_ok,
        celery=celery_ok,
    )
