"""Server-side PDF generation with notebook-style paper templates.

Uses ReportLab to create high-quality PDFs with:
  - Lined, blank, or grid paper backgrounds
  - Handwriting overlay from generated images
  - Multi-page support
  - Optional watermark
"""

from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader

logger = logging.getLogger(__name__)

# ─── Paper Colours ──────────────────────────────────────
PAPER_BG = Color(0.99, 0.99, 0.98)           # Warm white
LINE_COLOR = Color(0.82, 0.85, 0.90, 0.5)    # Light blue-grey
GRID_COLOR = Color(0.85, 0.87, 0.90, 0.35)   # Lighter grey
MARGIN_LINE_COLOR = Color(0.95, 0.65, 0.65, 0.6)  # Red margin


# ─── Paper Template Renderers ──────────────────────────
def _draw_lined_paper(
    c: rl_canvas.Canvas,
    width: float,
    height: float,
    line_spacing_mm: float = 8.0,
    margin_left_mm: float = 25.0,
) -> None:
    """Draw lined notebook paper with a red margin line."""
    # Background
    c.setFillColor(PAPER_BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Horizontal lines
    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.3)
    spacing = line_spacing_mm * mm
    top_margin = height - 25 * mm
    bottom_margin = 20 * mm

    y = top_margin
    while y > bottom_margin:
        c.line(15 * mm, y, width - 15 * mm, y)
        y -= spacing

    # Red margin line
    c.setStrokeColor(MARGIN_LINE_COLOR)
    c.setLineWidth(0.5)
    margin_x = margin_left_mm * mm
    c.line(margin_x, height - 10 * mm, margin_x, 10 * mm)


def _draw_grid_paper(
    c: rl_canvas.Canvas,
    width: float,
    height: float,
    grid_spacing_mm: float = 5.0,
) -> None:
    """Draw grid/graph paper."""
    c.setFillColor(PAPER_BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    c.setStrokeColor(GRID_COLOR)
    c.setLineWidth(0.2)
    spacing = grid_spacing_mm * mm
    margin = 15 * mm

    # Horizontal lines
    y = margin
    while y < height - margin:
        c.line(margin, y, width - margin, y)
        y += spacing

    # Vertical lines
    x = margin
    while x < width - margin:
        c.line(x, margin, x, height - margin)
        x += spacing


def _draw_blank_paper(
    c: rl_canvas.Canvas,
    width: float,
    height: float,
) -> None:
    """Draw blank white paper."""
    c.setFillColor(PAPER_BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)


# ─── Paper drawers lookup ──────────────────────────────
PAPER_DRAWERS = {
    "lined": _draw_lined_paper,
    "blank": _draw_blank_paper,
    "grid": _draw_grid_paper,
}


# ─── PDF Generator ─────────────────────────────────────
class PDFGenerator:
    """Generates notebook-style PDFs from handwriting page images."""

    def __init__(
        self,
        paper_style: str = "lined",
        page_size: tuple[float, float] = A4,
        line_spacing_mm: float = 8.0,
        watermark: bool = True,
    ):
        self.paper_style = paper_style
        self.page_size = page_size
        self.line_spacing_mm = line_spacing_mm
        self.watermark = watermark
        self.width, self.height = page_size

    def generate(
        self,
        handwriting_pages: list[Image.Image],
        output_path: Path,
    ) -> Path:
        """Compose handwriting images onto notebook paper and save as PDF.

        Args:
            handwriting_pages: List of RGBA PIL images with the handwriting.
            output_path: Path to save the PDF.

        Returns:
            Path to the generated PDF.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        c = rl_canvas.Canvas(str(output_path), pagesize=self.page_size)

        drawer = PAPER_DRAWERS.get(self.paper_style, _draw_lined_paper)

        for i, hw_page in enumerate(handwriting_pages):
            # Draw paper background
            if self.paper_style == "lined":
                drawer(c, self.width, self.height, self.line_spacing_mm)
            elif self.paper_style == "grid":
                drawer(c, self.width, self.height)
            else:
                drawer(c, self.width, self.height)

            # Overlay handwriting image
            # Convert RGBA to RGB with white background for PDF
            if hw_page.mode == "RGBA":
                bg = Image.new("RGBA", hw_page.size, (0, 0, 0, 0))
                composite = Image.alpha_composite(bg, hw_page)
                # Convert to RGB
                rgb_page = composite.convert("RGB")
            else:
                rgb_page = hw_page.convert("RGB")

            # Scale to fit page
            img_w, img_h = rgb_page.size
            scale_x = self.width / img_w
            scale_y = self.height / img_h
            scale = min(scale_x, scale_y)

            draw_w = img_w * scale
            draw_h = img_h * scale

            # Create an ImageReader from PIL image
            buf = BytesIO()
            rgb_page.save(buf, format="PNG")
            buf.seek(0)
            img_reader = ImageReader(buf)

            # Draw with transparency-like behaviour
            # (ReportLab doesn't support true RGBA overlay, so we use a mask approach)
            c.saveState()
            c.drawImage(
                img_reader,
                0,
                0,
                width=draw_w,
                height=draw_h,
                mask="auto",
                preserveAspectRatio=True,
            )
            c.restoreState()

            # Watermark
            if self.watermark:
                c.saveState()
                c.setFont("Helvetica", 6)
                c.setFillColor(Color(0.7, 0.7, 0.7, 0.3))
                c.drawString(
                    self.width - 120,
                    8,
                    "Generated by HandwritOCR",
                )
                c.restoreState()

            # Next page
            if i < len(handwriting_pages) - 1:
                c.showPage()

        c.save()
        logger.info(f"PDF generated: {output_path} ({len(handwriting_pages)} pages)")
        return output_path
