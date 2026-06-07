"""Celery task for handwriting generation.

Orchestrates the full pipeline:
  1. Extract style from samples (0–15%)
  2. Fine-tune ML model on user samples (15–40%)
  3. Generate handwriting pages (40–70%)
  4. Create PDF/PNG output (70–95%)
  5. Report progress via Redis
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ─── Progress Helper ───────────────────────────────────
def _update_progress(
    task_id: str,
    status: str,
    progress: int,
    step: str,
    download_url: str | None = None,
    error: str | None = None,
) -> None:
    """Store task progress in Redis for WebSocket to read."""
    try:
        import redis as redis_lib
        from app.config import settings

        r = redis_lib.from_url(settings.redis_url, socket_timeout=2)
        data = {
            "status": status,
            "progress": progress,
            "step": step,
            "download_url": download_url,
            "error": error,
        }
        r.setex(f"task:{task_id}:status", 3600, json.dumps(data))  # 1hr TTL
    except Exception as e:
        logger.warning(f"Failed to update progress in Redis: {e}")


# ─── Core Generation Logic ────────────────────────────
def run_generation_sync(task_id: str, params: dict) -> Path:
    """Run the full generation pipeline synchronously.

    This is used both by the Celery task and the sync fallback.

    Args:
        task_id: Unique task identifier.
        params: Dict with session_id, text, paper_style, font_size, line_spacing, export_format.

    Returns:
        Path to the generated output file.
    """
    from app.core.style_extractor import StyleExtractor
    from app.core.handwriting_gen import HandwritingGenerator
    from app.core.pdf_generator import PDFGenerator
    from app.storage.file_storage import (
        get_session_sample_paths,
        create_task_output_dir,
    )

    session_id = params["session_id"]
    text = params["text"]
    paper_style = params.get("paper_style", "lined")
    font_size = params.get("font_size", 18)
    line_spacing = params.get("line_spacing", 32)
    export_format = params.get("export_format", "pdf")

    output_dir = create_task_output_dir(task_id)

    # ── Step 1: Extract style (0–25%) ──────────────
    _update_progress(task_id, "processing", 5, "Loading samples...")
    sample_paths = get_session_sample_paths(session_id)

    _update_progress(task_id, "processing", 10, "Analysing handwriting style...")
    extractor = StyleExtractor(target_char_height=int(font_size * 2.5))
    profile = extractor.extract(sample_paths, output_dir)

    _update_progress(
        task_id, "processing", 15,
        f"Style extracted: {profile.total_chars_extracted} characters",
    )

    # ── Step 2: Fine-tune ML model if available (15–40%) ──
    _update_progress(task_id, "processing", 20, "Checking ML model...")
    try:
        from pathlib import Path as _Path
        base_ckpt = _Path("app/ml/checkpoints/best.pt")
        if base_ckpt.exists():
            _update_progress(task_id, "processing", 22, "Fine-tuning model on your handwriting...")
            from app.ml.fine_tune import FineTuner

            user_ckpt_dir = _Path("app/ml/checkpoints") / session_id
            user_ckpt_dir.mkdir(parents=True, exist_ok=True)
            user_ckpt_path = user_ckpt_dir / "user_model.pt"

            tuner = FineTuner(base_checkpoint=base_ckpt)
            tuner.fine_tune(
                sample_image_paths=sample_paths,
                num_iterations=80,
                learning_rate=1e-5,
                output_checkpoint=user_ckpt_path,
            )
            _update_progress(task_id, "processing", 40, "Model fine-tuned on your style!")
        else:
            _update_progress(task_id, "processing", 40, "Using procedural generation (no ML model)")
    except Exception as e:
        logger.warning(f"ML fine-tuning skipped: {e}")
        _update_progress(task_id, "processing", 40, "Using procedural generation")

    # ── Step 3: Generate handwriting (40–70%) ──────
    _update_progress(task_id, "processing", 45, "Generating handwriting...")

    # Scale font size and line spacing for 300 DPI
    dpi_scale = 300 / 72  # PDF points to pixels
    gen = HandwritingGenerator(
        profile=profile,
        font_size=int(font_size * dpi_scale),
        line_spacing=int(line_spacing * dpi_scale),
        session_id=session_id,
    )

    pages = gen.generate_pages(text)
    _update_progress(
        task_id, "processing", 70,
        f"Generated {len(pages)} page(s)",
    )

    # ── Step 3: Create output (70–95%) ─────────────
    if export_format == "png":
        _update_progress(task_id, "processing", 80, "Saving PNG...")
        # Save first page as PNG (or all pages)
        if len(pages) == 1:
            output_path = output_dir / "handwriting.png"
            # Composite on white background
            from PIL import Image

            bg = Image.new("RGB", pages[0].size, (252, 252, 250))
            bg.paste(pages[0], mask=pages[0].split()[3] if pages[0].mode == "RGBA" else None)
            bg.save(str(output_path), "PNG", dpi=(300, 300))
        else:
            # Save each page
            output_path = output_dir / "handwriting_page_001.png"
            for i, page in enumerate(pages):
                from PIL import Image

                p = output_dir / f"handwriting_page_{i + 1:03d}.png"
                bg = Image.new("RGB", page.size, (252, 252, 250))
                bg.paste(page, mask=page.split()[3] if page.mode == "RGBA" else None)
                bg.save(str(p), "PNG", dpi=(300, 300))
    else:
        _update_progress(task_id, "processing", 80, "Creating PDF...")
        pdf_gen = PDFGenerator(
            paper_style=paper_style,
            line_spacing_mm=line_spacing * 0.265,  # px to mm approximation
        )
        output_path = output_dir / "handwriting.pdf"
        pdf_gen.generate(pages, output_path)

    _update_progress(task_id, "processing", 95, "Finalising...")

    # ── Step 4: Complete ───────────────────────────
    download_url = f"/api/download/{task_id}"
    _update_progress(task_id, "completed", 100, "Complete", download_url=download_url)

    logger.info(f"Task {task_id} completed: {output_path}")
    return output_path


# ─── Celery Task ───────────────────────────────────────
try:
    from app.tasks.celery_app import celery_app

    @celery_app.task(
        name="app.tasks.generation_task.generate_handwriting_task",
        bind=True,
        max_retries=2,
    )
    def generate_handwriting_task(self, task_id: str, params: dict) -> str:
        """Celery task wrapper for handwriting generation."""
        try:
            output_path = run_generation_sync(task_id, params)
            return str(output_path)
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            _update_progress(task_id, "failed", 0, "Failed", error=str(e))
            raise

except ImportError:
    logger.warning("Celery not available — generation will run synchronously")
