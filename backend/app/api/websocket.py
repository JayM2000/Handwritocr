"""WebSocket endpoint for real-time generation progress updates."""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/progress/{task_id}")
async def progress_websocket(websocket: WebSocket, task_id: str) -> None:
    """Stream generation progress updates to the client.

    Reads task progress from Redis and sends JSON messages:
      { "task_id": "...", "status": "processing", "progress": 45, "step": "..." }

    On completion:
      { "task_id": "...", "status": "completed", "progress": 100, "download_url": "..." }
    """
    await websocket.accept()
    logger.info(f"WebSocket connected: task {task_id}")

    try:
        # Try to connect to Redis for progress polling
        redis_client = None
        try:
            import redis as redis_lib
            from app.config import settings

            redis_client = redis_lib.from_url(settings.redis_url, socket_timeout=2)
            redis_client.ping()
        except Exception:
            logger.warning("Redis unavailable for WebSocket progress")
            # Send a fallback message
            await websocket.send_json({
                "task_id": task_id,
                "status": "processing",
                "progress": 0,
                "step": "Processing (progress unavailable without Redis)",
            })

        # Poll for updates
        last_progress = -1
        max_polls = 600  # 5 minutes at 500ms intervals
        poll_count = 0

        while poll_count < max_polls:
            poll_count += 1

            if redis_client:
                try:
                    data = redis_client.get(f"task:{task_id}:status")
                    if data:
                        info = json.loads(data)
                        progress = info.get("progress", 0)

                        # Only send if progress changed
                        if progress != last_progress:
                            await websocket.send_json({
                                "task_id": task_id,
                                "status": info.get("status", "processing"),
                                "progress": progress,
                                "step": info.get("step", ""),
                                "download_url": info.get("download_url"),
                                "error": info.get("error"),
                            })
                            last_progress = progress

                        # Done?
                        status = info.get("status", "")
                        if status in ("completed", "failed"):
                            break
                except Exception as e:
                    logger.warning(f"Redis read error: {e}")
            else:
                # Without Redis, check if output file exists
                try:
                    from app.storage.file_storage import get_task_output_dir

                    output_dir = get_task_output_dir(task_id)
                    if list(output_dir.glob("handwriting.*")):
                        await websocket.send_json({
                            "task_id": task_id,
                            "status": "completed",
                            "progress": 100,
                            "step": "Complete",
                            "download_url": f"/api/download/{task_id}",
                        })
                        break
                except FileNotFoundError:
                    pass

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "task_id": task_id,
                "status": "failed",
                "progress": 0,
                "error": str(e),
            })
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
