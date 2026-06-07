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


def _draw_dotted_paper(
    c: rl_canvas.Canvas,
    width: float,
    height: float,
    dot_spacing_mm: float = 5.0,
) -> None:
    """Draw dot grid paper (dots at grid intersections)."""
    c.setFillColor(PAPER_BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    dot_color = Color(0.75, 0.78, 0.82, 0.6)
    c.setFillColor(dot_color)
    spacing = dot_spacing_mm * mm
    margin = 15 * mm
    dot_radius = 0.4 * mm

    y = margin
    while y < height - margin:
        x = margin
        while x < width - margin:
            c.circle(x, y, dot_radius, fill=True, stroke=False)
            x += spacing
        y += spacing


def _draw_cornell_paper(
    c: rl_canvas.Canvas,
    width: float,
    height: float,
) -> None:
    """Draw Cornell note-taking style paper (cue column + summary row)."""
    c.setFillColor(PAPER_BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Cue column divider (left, ~62mm from left edge)
    cue_x = 62 * mm
    c.setStrokeColor(Color(0.85, 0.55, 0.55, 0.5))
    c.setLineWidth(0.6)
    c.line(cue_x, 20 * mm, cue_x, height - 15 * mm)

    # Summary area divider (bottom, ~50mm from bottom)
    summary_y = 50 * mm
    c.line(15 * mm, summary_y, width - 15 * mm, summary_y)

    # Horizontal ruled lines in the notes area
    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.25)
    line_spacing = 7.5 * mm
    y = height - 25 * mm
    while y > summary_y + 5 * mm:
        c.line(cue_x + 3 * mm, y, width - 15 * mm, y)
        y -= line_spacing

    # Lighter lines in cue column
    c.setStrokeColor(Color(0.88, 0.90, 0.92, 0.3))
    y = height - 25 * mm
    while y > summary_y + 5 * mm:
        c.line(15 * mm, y, cue_x - 3 * mm, y)
        y -= line_spacing * 2  # Wider spacing in cue column

    # Labels (very faint)
    c.setFillColor(Color(0.8, 0.8, 0.8, 0.3))
    c.setFont("Helvetica", 6)
    c.drawString(20 * mm, height - 12 * mm, "Cue Column")
    c.drawString(cue_x + 5 * mm, height - 12 * mm, "Notes")
    c.drawString(20 * mm, summary_y - 8 * mm + 50 * mm, "Summary")


def _draw_margin_ruled_paper(
    c: rl_canvas.Canvas,
    width: float,
    height: float,
    line_spacing_mm: float = 9.0,
) -> None:
    """Draw wide ruled paper with double margin lines."""
    c.setFillColor(PAPER_BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Horizontal ruled lines (wider spacing than standard)
    c.setStrokeColor(Color(0.80, 0.83, 0.88, 0.45))
    c.setLineWidth(0.25)
    spacing = line_spacing_mm * mm
    top_margin = height - 30 * mm
    bottom_margin = 20 * mm

    y = top_margin
    while y > bottom_margin:
        c.line(32 * mm, y, width - 15 * mm, y)
        y -= spacing

    # Double margin lines (red)
    c.setStrokeColor(MARGIN_LINE_COLOR)
    c.setLineWidth(0.4)
    margin_x1 = 27 * mm
    margin_x2 = 29 * mm
    c.line(margin_x1, height - 10 * mm, margin_x1, 10 * mm)
    c.line(margin_x2, height - 10 * mm, margin_x2, 10 * mm)

    # Header line
    c.setStrokeColor(Color(0.75, 0.78, 0.82, 0.5))
    c.setLineWidth(0.5)
    c.line(15 * mm, height - 25 * mm, width - 15 * mm, height - 25 * mm)


def _draw_engineering_paper(
    c: rl_canvas.Canvas,
    width: float,
    height: float,
    grid_spacing_mm: float = 5.0,
) -> None:
    """Draw engineering pad style paper (green-tint with 5×5 grid)."""
    # Light green-tinted background
    eng_bg = Color(0.96, 0.99, 0.96)
    c.setFillColor(eng_bg)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    margin = 15 * mm
    spacing = grid_spacing_mm * mm

    # Minor grid lines (every 1 unit)
    c.setStrokeColor(Color(0.78, 0.90, 0.80, 0.3))
    c.setLineWidth(0.15)

    y = margin
    while y < height - margin:
        c.line(margin, y, width - margin, y)
        y += spacing

    x = margin
    while x < width - margin:
        c.line(x, margin, x, height - margin)
        x += spacing

    # Major grid lines (every 5 units)
    c.setStrokeColor(Color(0.55, 0.78, 0.60, 0.5))
    c.setLineWidth(0.35)
    major_spacing = spacing * 5

    y = margin
    while y < height - margin:
        c.line(margin, y, width - margin, y)
        y += major_spacing

    x = margin
    while x < width - margin:
        c.line(x, margin, x, height - margin)
        x += major_spacing


def _draw_vintage_paper(
    c: rl_canvas.Canvas,
    width: float,
    height: float,
) -> None:
    """Draw aged/yellowed vintage paper with subtle stain effects."""
    import random as _rng

    # Warm aged paper background
    vintage_bg = Color(0.97, 0.94, 0.87)
    c.setFillColor(vintage_bg)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Subtle edge darkening (vignette effect)
    vignette = Color(0.85, 0.80, 0.70, 0.15)
    c.setFillColor(vignette)
    # Top strip
    c.rect(0, height - 12 * mm, width, 12 * mm, fill=True, stroke=False)
    # Bottom strip
    c.rect(0, 0, width, 12 * mm, fill=True, stroke=False)
    # Left strip
    c.rect(0, 0, 8 * mm, height, fill=True, stroke=False)
    # Right strip
    c.rect(width - 8 * mm, 0, 8 * mm, height, fill=True, stroke=False)

    # Subtle coffee-stain-like circles (2–4 random spots)
    _rng.seed(42)  # Deterministic for consistency
    for _ in range(3):
        cx = _rng.uniform(30, float(width / mm) - 30) * mm
        cy = _rng.uniform(30, float(height / mm) - 30) * mm
        r = _rng.uniform(12, 28) * mm
        stain_color = Color(
            0.88 + _rng.uniform(-0.03, 0.03),
            0.82 + _rng.uniform(-0.03, 0.03),
            0.72 + _rng.uniform(-0.03, 0.03),
            _rng.uniform(0.04, 0.10),
        )
        c.setFillColor(stain_color)
        c.setStrokeColor(stain_color)
        c.setLineWidth(0)
        c.circle(cx, cy, r, fill=True, stroke=False)

    # Faint ruled lines (as if faded with age)
    c.setStrokeColor(Color(0.80, 0.75, 0.65, 0.25))
    c.setLineWidth(0.2)
    spacing = 8 * mm
    y = height - 30 * mm
    while y > 25 * mm:
        c.line(20 * mm, y, width - 20 * mm, y)
        y -= spacing

    _rng.seed()  # Reset seed


# ─── Paper drawers lookup ──────────────────────────────
PAPER_DRAWERS = {
    "lined": _draw_lined_paper,
    "blank": _draw_blank_paper,
    "grid": _draw_grid_paper,
    "dotted": _draw_dotted_paper,
    "cornell": _draw_cornell_paper,
    "margin_ruled": _draw_margin_ruled_paper,
    "engineering": _draw_engineering_paper,
    "vintage": _draw_vintage_paper,
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
