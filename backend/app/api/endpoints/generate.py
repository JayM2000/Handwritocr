"""Generate handwriting endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    GenerateRequest,
    GenerateResponse,
    TaskStatus,
    TaskStatusResponse,
)
from app.storage.file_storage import (
    get_session_sample_paths,
    generate_task_id,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _try_celery_dispatch(task_id: str, request: GenerateRequest) -> bool:
    """Try to dispatch generation to Celery. Returns False if Celery unavailable."""
    try:
        from app.tasks.generation_task import generate_handwriting_task

        generate_handwriting_task.apply_async(
            args=[task_id, request.model_dump()],
            task_id=task_id,
        )
        return True
    except Exception as e:
        logger.warning(f"Celery dispatch failed, falling back to sync: {e}")
        return False


def _run_sync(task_id: str, request: GenerateRequest) -> None:
    """Run generation synchronously when Celery is unavailable."""
    from app.tasks.generation_task import run_generation_sync

    run_generation_sync(task_id, request.model_dump())


@router.post("/generate", response_model=GenerateResponse, tags=["generation"])
async def generate_handwriting(request: GenerateRequest) -> GenerateResponse:
    """Start handwriting generation.

    Submits a Celery task for async processing. If Celery is unavailable,
    falls back to synchronous processing.
    """
    # Validate session exists and has samples
    try:
        sample_paths = get_session_sample_paths(request.session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")

    if not sample_paths:
        raise HTTPException(
            status_code=400, detail="No samples found for this session"
        )

    task_id = generate_task_id()

    # Try Celery first, fall back to sync
    if _try_celery_dispatch(task_id, request):
        return GenerateResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="Generation task queued (async)",
        )
    else:
        # Synchronous fallback
        try:
            _run_sync(task_id, request)
            return GenerateResponse(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                message="Generation completed (sync mode)",
            )
        except Exception as e:
            logger.error(f"Sync generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/generate/{task_id}/status",
    response_model=TaskStatusResponse,
    tags=["generation"],
)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Check the status of a generation task."""
    try:
        import redis as redis_lib
        from app.config import settings
        import json

        r = redis_lib.from_url(settings.redis_url, socket_timeout=2)
        data = r.get(f"task:{task_id}:status")
        if data:
            info = json.loads(data)
            return TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus(info.get("status", "pending")),
                progress=info.get("progress", 0),
                step=info.get("step", ""),
                download_url=info.get("download_url"),
                error=info.get("error"),
            )
    except Exception:
        pass

    # Check if output file exists (sync mode fallback)
    try:
        from app.storage.file_storage import get_task_output_dir

        output_dir = get_task_output_dir(task_id)
        output_files = list(output_dir.glob("handwriting.*"))
        if output_files:
            return TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                progress=100,
                step="Complete",
                download_url=f"/api/download/{task_id}",
            )
    except FileNotFoundError:
        pass

    return TaskStatusResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        progress=0,
        step="Waiting...",
    )
