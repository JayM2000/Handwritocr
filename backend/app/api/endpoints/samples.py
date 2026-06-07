"""Sample upload endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image as PILImage

from app.config import settings
from app.models.schemas import UploadResponse, SampleInfo
from app.storage.file_storage import create_session, get_session_dir

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/samples/upload", response_model=UploadResponse, tags=["samples"])
async def upload_samples(
    files: list[UploadFile] = File(..., description="Handwriting sample images"),
) -> UploadResponse:
    """Upload handwriting sample images for style extraction.

    Accepts PNG, JPG, WebP images. Preprocesses and saves to a session directory.
    Returns a session_id for use in subsequent API calls.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > settings.max_samples_per_session:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.max_samples_per_session} samples allowed",
        )

    # Create session
    session_id = create_session()
    session_dir = get_session_dir(session_id)
    samples: list[SampleInfo] = []

    allowed_types = {"image/png", "image/jpeg", "image/webp", "image/bmp"}

    for i, file in enumerate(files):
        # Validate content type
        if file.content_type and file.content_type not in allowed_types:
            logger.warning(f"Rejected file {file.filename}: {file.content_type}")
            continue

        # Read and validate size
        content = await file.read()
        if len(content) > settings.max_upload_bytes:
            logger.warning(f"File too large: {file.filename} ({len(content)} bytes)")
            continue

        # Save original
        ext = file.filename.rsplit(".", 1)[-1] if file.filename else "png"
        save_name = f"sample_{i:03d}.{ext}"
        save_path = session_dir / save_name

        with open(save_path, "wb") as f:
            f.write(content)

        # Get image dimensions
        try:
            with PILImage.open(save_path) as img:
                width, height = img.size
        except Exception:
            save_path.unlink(missing_ok=True)
            continue

        samples.append(
            SampleInfo(
                filename=save_name,
                size_bytes=len(content),
                width=width,
                height=height,
            )
        )

    if not samples:
        raise HTTPException(
            status_code=400,
            detail="No valid image files were uploaded",
        )

    logger.info(f"Session {session_id}: {len(samples)} samples uploaded")

    return UploadResponse(
        session_id=session_id,
        samples=samples,
        total_samples=len(samples),
    )
