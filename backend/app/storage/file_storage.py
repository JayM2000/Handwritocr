"""File storage management for uploads and generated outputs."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from app.config import settings


def create_session() -> str:
    """Create a new upload session and return its ID."""
    session_id = uuid.uuid4().hex[:12]
    session_dir = settings.upload_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_id


def get_session_dir(session_id: str) -> Path:
    """Get the upload directory for a session."""
    d = settings.upload_dir / session_id
    if not d.exists():
        raise FileNotFoundError(f"Session {session_id} not found")
    return d


def get_session_sample_paths(session_id: str) -> list[str]:
    """List all sample image paths in a session."""
    d = get_session_dir(session_id)
    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    return [
        str(f) for f in sorted(d.iterdir())
        if f.suffix.lower() in exts
    ]


def create_task_output_dir(task_id: str) -> Path:
    """Create an output directory for a generation task."""
    d = settings.output_dir / task_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_task_output_dir(task_id: str) -> Path:
    """Get the output directory for a task."""
    d = settings.output_dir / task_id
    if not d.exists():
        raise FileNotFoundError(f"Task output {task_id} not found")
    return d


def get_output_file(task_id: str, filename: str) -> Path:
    """Get a specific output file for a task."""
    f = settings.output_dir / task_id / filename
    if not f.exists():
        raise FileNotFoundError(f"Output file not found: {f}")
    return f


def cleanup_session(session_id: str) -> None:
    """Remove a session's uploaded files."""
    d = settings.upload_dir / session_id
    if d.exists():
        shutil.rmtree(d)


def cleanup_task(task_id: str) -> None:
    """Remove a task's output files."""
    d = settings.output_dir / task_id
    if d.exists():
        shutil.rmtree(d)


def generate_task_id() -> str:
    """Generate a unique task ID."""
    return uuid.uuid4().hex[:16]
