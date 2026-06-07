"""Handwriting generation engine.

Takes a style profile and input text, then generates realistic handwriting
images using a hybrid approach:
  1. If extracted glyphs exist → use actual character crops with randomised placement
  2. Fallback → render with a handwriting font + procedural randomness

Natural variation is added via Gaussian noise on spacing, baseline, size, and slant.
"""

from __future__ import annotations

import logging
import math
import os
import random
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .style_extractor import StyleProfile

logger = logging.getLogger(__name__)

# ─── Constants ──────────────────────────────────────────
DEFAULT_PAGE_WIDTH = 2480   # A4 at 300 DPI
DEFAULT_PAGE_HEIGHT = 3508
DEFAULT_MARGIN_LEFT = 200
DEFAULT_MARGIN_RIGHT = 150
DEFAULT_MARGIN_TOP = 200
DEFAULT_MARGIN_BOTTOM = 200

# Path to a bundled handwriting font (fallback)
FALLBACK_FONT_DIR = Path(__file__).parent.parent.parent / "assets" / "fonts"


def _get_fallback_font(size: int = 36) -> ImageFont.FreeTypeFont:
    """Load a handwriting-style font for fallback rendering."""
    font_paths = [
        FALLBACK_FONT_DIR / "Caveat-Regular.ttf",
        FALLBACK_FONT_DIR / "Caveat-Medium.ttf",
    ]
    for fp in font_paths:
        if fp.exists():
            return ImageFont.truetype(str(fp), size)

    # Last resort: try system fonts
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


# ─── Glyph-based Generator ─────────────────────────────
class GlyphRenderer:
    """Renders text using extracted glyph images with natural variation."""

    def __init__(self, profile: StyleProfile):
        self.profile = profile
        self.glyphs: list[np.ndarray] = []
        self._load_glyphs()

    def _load_glyphs(self) -> None:
        """Load extracted glyph images from the style profile directory."""
        glyph_dir = Path(self.profile.glyph_dir)
        if not glyph_dir.exists():
            return

        for glyph_file in sorted(glyph_dir.glob("glyph_*.png")):
            img = cv2.imread(str(glyph_file), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                self.glyphs.append(img)

        logger.info(f"Loaded {len(self.glyphs)} glyphs for rendering")

    def has_glyphs(self) -> bool:
        return len(self.glyphs) >= 10

    def get_random_glyph(self) -> np.ndarray:
        """Return a random glyph image."""
        return random.choice(self.glyphs)


# ─── Page Generator ────────────────────────────────────
class HandwritingGenerator:
    """Generates handwriting images from text + style profile."""

    def __init__(
        self,
        profile: StyleProfile,
        page_width: int = DEFAULT_PAGE_WIDTH,
        page_height: int = DEFAULT_PAGE_HEIGHT,
        margin_left: int = DEFAULT_MARGIN_LEFT,
        margin_right: int = DEFAULT_MARGIN_RIGHT,
        margin_top: int = DEFAULT_MARGIN_TOP,
        margin_bottom: int = DEFAULT_MARGIN_BOTTOM,
        font_size: int = 36,
        line_spacing: int = 60,
        ink_color: tuple[int, int, int] = (20, 20, 50),
    ):
        self.profile = profile
        self.page_width = page_width
        self.page_height = page_height
        self.margin_left = margin_left
        self.margin_right = margin_right
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.font_size = font_size
        self.line_spacing = line_spacing
        self.ink_color = ink_color

        self.content_width = page_width - margin_left - margin_right
        self.content_height = page_height - margin_top - margin_bottom

        self.glyph_renderer = GlyphRenderer(profile)

    def generate_pages(self, text: str) -> list[Image.Image]:
        """Generate handwriting pages from input text.

        Returns list of PIL Images, one per page.
        """
        if self.glyph_renderer.has_glyphs():
            return self._generate_with_glyphs(text)
        else:
            return self._generate_with_font(text)

    # ─── Font-based rendering (fallback) ────────────
    def _generate_with_font(self, text: str) -> list[Image.Image]:
        """Render text using a handwriting font with procedural randomness."""
        font = _get_fallback_font(self.font_size)
        pages: list[Image.Image] = []
        paragraphs = text.split("\n")

        x = self.margin_left
        y = self.margin_top
        page = Image.new("RGBA", (self.page_width, self.page_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(page)

        for para in paragraphs:
            if not para.strip():
                y += self.line_spacing
                if y > self.page_height - self.margin_bottom:
                    pages.append(page)
                    page = Image.new("RGBA", (self.page_width, self.page_height), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(page)
                    y = self.margin_top
                continue

            words = para.split()
            for word in words:
                # Measure word width
                bbox = font.getbbox(word)
                word_width = bbox[2] - bbox[0]

                # Line wrap
                if x + word_width > self.page_width - self.margin_right:
                    x = self.margin_left
                    y += self.line_spacing + random.gauss(0, 2)

                    if y > self.page_height - self.margin_bottom:
                        pages.append(page)
                        page = Image.new("RGBA", (self.page_width, self.page_height), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(page)
                        y = self.margin_top

                # Draw each character with individual variation
                for char in word:
                    # Natural variation
                    dx = random.gauss(0, 1.2)        # Horizontal jitter
                    dy = random.gauss(0, 1.5)        # Baseline wobble
                    size_var = random.gauss(1.0, 0.03)  # Size variation ±3%

                    # Slight ink opacity variation
                    alpha = max(150, min(255, int(random.gauss(220, 15))))
                    color = (*self.ink_color, alpha)

                    char_font = font
                    char_x = int(x + dx)
                    char_y = int(y + dy)

                    draw.text(
                        (char_x, char_y),
                        char,
                        font=char_font,
                        fill=color,
                    )

                    # Advance cursor
                    char_bbox = font.getbbox(char)
                    char_w = char_bbox[2] - char_bbox[0]
                    spacing_noise = random.gauss(0, 1.5)
                    x += char_w * size_var + spacing_noise

                # Word spacing
                x += self.font_size * 0.4 + random.gauss(0, 2)

            # End of paragraph → new line
            x = self.margin_left + random.gauss(0, 3)
            y += self.line_spacing + random.gauss(0, 2)

            if y > self.page_height - self.margin_bottom:
                pages.append(page)
                page = Image.new("RGBA", (self.page_width, self.page_height), (0, 0, 0, 0))
                draw = ImageDraw.Draw(page)
                y = self.margin_top

        # Don't forget the last page
        pages.append(page)
        return pages

    # ─── Glyph-based rendering ──────────────────────
    def _generate_with_glyphs(self, text: str) -> list[Image.Image]:
        """Render text using extracted glyph images with natural placement."""
        p = self.profile
        pages: list[Image.Image] = []
        page = Image.new("RGBA", (self.page_width, self.page_height), (0, 0, 0, 0))

        x = self.margin_left
        y = self.margin_top
        target_h = int(p.avg_char_height * 1.5)

        for char in text:
            if char == "\n":
                x = self.margin_left + random.gauss(0, 3)
                y += self.line_spacing + random.gauss(0, p.char_height_std * 0.3)

                if y > self.page_height - self.margin_bottom:
                    pages.append(page)
                    page = Image.new("RGBA", (self.page_width, self.page_height), (0, 0, 0, 0))
                    y = self.margin_top
                continue

            if char == " ":
                x += p.avg_word_spacing + random.gauss(0, p.char_spacing_std)
                continue

            # Pick a random glyph
            glyph = self.glyph_renderer.get_random_glyph()

            # Size variation
            scale = random.gauss(1.0, 0.05)
            glyph_h = max(10, int(target_h * scale))
            glyph_w = max(5, int(glyph.shape[1] * (glyph_h / max(1, glyph.shape[0]))))
            glyph_resized = cv2.resize(glyph, (glyph_w, glyph_h))

            # Line wrap
            if x + glyph_w > self.page_width - self.margin_right:
                x = self.margin_left + random.gauss(0, 3)
                y += self.line_spacing + random.gauss(0, 2)

                if y > self.page_height - self.margin_bottom:
                    pages.append(page)
                    page = Image.new("RGBA", (self.page_width, self.page_height), (0, 0, 0, 0))
                    y = self.margin_top

            # Baseline wobble
            dy = int(random.gauss(0, p.char_height_std * 0.15))
            place_y = y + dy

            # Slant
            slant = random.gauss(p.avg_slant_angle, p.slant_angle_std * 0.3)
            if abs(slant) > 0.5:
                M = np.float32([[1, math.tan(math.radians(slant)), 0], [0, 1, 0]])
                glyph_resized = cv2.warpAffine(
                    glyph_resized, M, (glyph_w + 10, glyph_h),
                    borderValue=0,
                )

            # Convert glyph to RGBA and composite onto page
            glyph_pil = Image.fromarray(glyph_resized).convert("L")
            alpha = max(160, min(255, int(random.gauss(210, 20))))
            ink_layer = Image.new("RGBA", glyph_pil.size, (*self.ink_color, 0))
            mask = glyph_pil.point(lambda p: min(p, alpha))
            ink_layer.putalpha(mask)

            # Paste
            px = int(x)
            py = int(place_y)
            if 0 <= px < self.page_width and 0 <= py < self.page_height:
                page.paste(ink_layer, (px, py), ink_layer)

            # Advance cursor
            x += glyph_w + p.avg_char_spacing + random.gauss(0, p.char_spacing_std * 0.5)

        pages.append(page)
        return pages
