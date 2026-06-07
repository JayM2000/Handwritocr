"""Stroke-to-image renderer.

Converts stroke sequences (dx, dy, pen_up) to PIL Images with:
  - Anti-aliased line rendering
  - Variable stroke width based on velocity
  - Ink color and opacity variation
  - Scaling to target page dimensions
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

from .utils import strokes_to_points


class StrokeRenderer:
    """Renders stroke data as PIL Images."""

    def __init__(
        self,
        width: int = 2480,
        height: int = 3508,
        margin_left: int = 200,
        margin_right: int = 150,
        margin_top: int = 200,
        margin_bottom: int = 200,
        ink_color: tuple[int, int, int] = (20, 20, 50),
        base_stroke_width: float = 3.0,
        line_spacing: int = 60,
    ):
        self.width = width
        self.height = height
        self.margin_left = margin_left
        self.margin_right = margin_right
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.ink_color = ink_color
        self.base_stroke_width = base_stroke_width
        self.line_spacing = line_spacing

    def render(
        self,
        strokes: np.ndarray,
        scale: float = 5.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
    ) -> Image.Image:
        """Render stroke data to a PIL RGBA Image.

        Args:
            strokes: Array of (dx, dy, pen_up), shape (N, 3).
            scale: Scaling factor for stroke coordinates.
            offset_x: Horizontal offset from left margin.
            offset_y: Vertical offset from top margin.

        Returns:
            PIL Image with rendered strokes on transparent background.
        """
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Convert offsets to absolute point sequences
        point_sequences = strokes_to_points(strokes)

        if not point_sequences:
            return img

        # Find bounding box for scaling
        all_x = [p[0] for seq in point_sequences for p in seq]
        all_y = [p[1] for seq in point_sequences for p in seq]

        if not all_x:
            return img

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        # Available content area
        content_w = self.width - self.margin_left - self.margin_right
        content_h = self.height - self.margin_top - self.margin_bottom

        # Compute scale to fit
        stroke_w = (max_x - min_x) * scale if max_x > min_x else 1
        stroke_h = (max_y - min_y) * scale if max_y > min_y else 1

        fit_scale_x = content_w / stroke_w if stroke_w > 0 else 1
        fit_scale_y = content_h / stroke_h if stroke_h > 0 else 1
        fit_scale = min(fit_scale_x, fit_scale_y, 1.0)  # Don't upscale

        final_scale = scale * fit_scale

        # Render each stroke
        for seq in point_sequences:
            if len(seq) < 2:
                continue

            for i in range(1, len(seq)):
                x0 = (seq[i - 1][0] - min_x) * final_scale + self.margin_left + offset_x
                y0 = (seq[i - 1][1] - min_y) * final_scale + self.margin_top + offset_y
                x1 = (seq[i][0] - min_x) * final_scale + self.margin_left + offset_x
                y1 = (seq[i][1] - min_y) * final_scale + self.margin_top + offset_y

                # Variable stroke width based on velocity
                dx = x1 - x0
                dy = y1 - y0
                velocity = math.sqrt(dx * dx + dy * dy) + 1e-6
                width = max(1, self.base_stroke_width * (1.0 + 2.0 / velocity))
                width = min(width, self.base_stroke_width * 3)

                # Slight opacity variation
                alpha = max(160, min(240, int(200 + 20 * math.sin(i * 0.3))))
                color = (*self.ink_color, alpha)

                # Draw anti-aliased line segment
                draw.line(
                    [(x0, y0), (x1, y1)],
                    fill=color,
                    width=max(1, int(width)),
                    joint="curve",
                )

        return img

    def render_multiline(
        self,
        line_strokes: list[np.ndarray],
        scale: float = 5.0,
    ) -> list[Image.Image]:
        """Render multiple lines of strokes across pages.

        Args:
            line_strokes: List of stroke arrays, one per text line.
            scale: Scaling factor.

        Returns:
            List of PIL Images (one per page).
        """
        pages: list[Image.Image] = []
        page = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(page)

        y_cursor = self.margin_top

        for line_stroke in line_strokes:
            if len(line_stroke) == 0:
                y_cursor += self.line_spacing
                continue

            # Render this line
            line_img = self.render(
                line_stroke,
                scale=scale,
                offset_y=y_cursor - self.margin_top,
            )

            # Check if we need a new page
            y_cursor += self.line_spacing

            if y_cursor > self.height - self.margin_bottom:
                pages.append(page)
                page = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
                y_cursor = self.margin_top

            # Composite line onto page
            page = Image.alpha_composite(page, line_img)

        pages.append(page)
        return pages
