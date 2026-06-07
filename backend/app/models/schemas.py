"""Pydantic schemas for API request/response models."""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


# ─── Enums ──────────────────────────────────────────────
class PaperStyle(str, Enum):
    LINED = "lined"
    BLANK = "blank"
    GRID = "grid"


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportFormat(str, Enum):
    PDF = "pdf"
    PNG = "png"


# ─── Request Models ────────────────────────────────────
class GenerateRequest(BaseModel):
    """Request body for POST /api/generate."""

    session_id: str = Field(..., description="Session ID from sample upload")
    text: str = Field(..., min_length=1, max_length=50000, description="Text to convert")
    paper_style: PaperStyle = Field(default=PaperStyle.LINED)
    font_size: int = Field(default=18, ge=10, le=36)
    line_spacing: int = Field(default=32, ge=20, le=60)
    export_format: ExportFormat = Field(default=ExportFormat.PDF)


# ─── Response Models ───────────────────────────────────
class HealthResponse(BaseModel):
    status: str = "ok"
    redis: bool = False
    celery: bool = False
    version: str = "0.1.0"


class SampleInfo(BaseModel):
    filename: str
    size_bytes: int
    width: int
    height: int


class UploadResponse(BaseModel):
    session_id: str
    samples: list[SampleInfo]
    total_samples: int
    message: str = "Samples uploaded successfully"


class GenerateResponse(BaseModel):
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    message: str = "Generation task queued"


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: int = Field(default=0, ge=0, le=100)
    step: str = ""
    download_url: str | None = None
    error: str | None = None


class ProgressMessage(BaseModel):
    """WebSocket progress message format."""

    task_id: str
    status: TaskStatus
    progress: int = 0
    step: str = ""
    download_url: str | None = None
    error: str | None = None
