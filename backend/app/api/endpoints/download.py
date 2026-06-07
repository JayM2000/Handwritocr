"""Download generated files endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.storage.file_storage import get_task_output_dir

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/download/{task_id}", tags=["download"])
async def download_file(task_id: str, format: str = "pdf") -> FileResponse:
    """Download the generated handwriting file.

    Args:
        task_id: The generation task ID.
        format: Output format — 'pdf' or 'png'.
    """
    try:
        output_dir = get_task_output_dir(task_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Task output not found")

    # Find the output file
    if format == "png":
        candidates = list(output_dir.glob("handwriting*.png"))
        media_type = "image/png"
        filename = "handwriting.png"
    else:
        candidates = list(output_dir.glob("handwriting*.pdf"))
        media_type = "application/pdf"
        filename = "handwriting.pdf"

    if not candidates:
        # Try alternative formats
        all_files = list(output_dir.iterdir())
        if all_files:
            file_path = all_files[0]
            filename = file_path.name
            media_type = "application/octet-stream"
        else:
            raise HTTPException(
                status_code=404, detail=f"No {format} output found for this task"
            )
    else:
        file_path = candidates[0]

    logger.info(f"Serving download: {file_path}")

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
