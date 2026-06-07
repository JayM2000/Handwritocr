"""Handwriting style extraction from sample images.

Analyses uploaded handwriting samples to build a style profile that
captures the unique characteristics of the user's writing:
  - Character dimensions & aspect ratios
  - Spacing statistics (mean, std)
  - Slant angle distribution
  - Stroke thickness
  - Individual character glyph crops
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path

import cv2
import numpy as np

from .image_utils import (
    load_and_preprocess,
    correct_skew,
    segment_lines,
    segment_characters,
    compute_stroke_width,
    compute_slant_angle,
    resize_char_to_height,
    score_image_quality,
    augment_glyph,
)

logger = logging.getLogger(__name__)

# ─── Style Profile Data ────────────────────────────────
@dataclass
class CharacterMetrics:
    """Metrics for a single extracted character."""

    width: int
    height: int
    aspect_ratio: float
    stroke_width: float


@dataclass
class StyleProfile:
    """Complete handwriting style profile extracted from samples."""

    # Character dimensions
    avg_char_height: float = 0.0
    avg_char_width: float = 0.0
    char_height_std: float = 0.0
    char_width_std: float = 0.0

    # Spacing
    avg_char_spacing: float = 0.0
    char_spacing_std: float = 0.0
    avg_word_spacing: float = 0.0
    avg_line_spacing: float = 0.0

    # Style
    avg_slant_angle: float = 0.0
    slant_angle_std: float = 0.0
    avg_stroke_width: float = 2.0
    stroke_width_std: float = 0.5

    # Character count
    total_chars_extracted: int = 0
    total_lines_extracted: int = 0

    # Glyph image paths (stored separately)
    glyph_dir: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: Path) -> "StyleProfile":
        data = json.loads(path.read_text())
        return cls(**data)

    @property
    def consistency_score(self) -> float:
        """How consistent the user's writing is (0–1, higher = more consistent)."""
        if self.avg_char_height < 1:
            return 0.5
        h_cv = self.char_height_std / max(self.avg_char_height, 1)
        w_cv = self.char_width_std / max(self.avg_char_width, 1)
        s_cv = self.slant_angle_std / max(abs(self.avg_slant_angle) + 1, 1)
        avg_cv = (h_cv + w_cv + s_cv) / 3
        return max(0.0, min(1.0, 1.0 - avg_cv))


# ─── Style Extractor ───────────────────────────────────
class StyleExtractor:
    """Extracts handwriting style from sample images."""

    def __init__(self, target_char_height: int = 48):
        self.target_char_height = target_char_height

    def extract(
        self,
        sample_paths: list[str],
        output_dir: Path,
    ) -> StyleProfile:
        """Analyse multiple handwriting samples and build a style profile.

        Args:
            sample_paths: Paths to sample images.
            output_dir: Directory to store extracted glyphs.

        Returns:
            A StyleProfile containing all extracted metrics.
        """
        glyph_dir = output_dir / "glyphs"
        glyph_dir.mkdir(parents=True, exist_ok=True)

        all_char_widths: list[float] = []
        all_char_heights: list[float] = []
        all_spacings: list[float] = []
        all_slants: list[float] = []
        all_stroke_widths: list[float] = []
        all_line_spacings: list[float] = []
        glyph_index = 0
        total_lines = 0

        for sample_path in sample_paths:
            # Quality check — skip poor samples
            quality = score_image_quality(sample_path)
            if not quality["usable"]:
                logger.warning(
                    f"Skipping low-quality sample {sample_path}: {quality['feedback']}"
                )
                continue
            logger.info(
                f"Sample {sample_path}: quality={quality['overall']:.2f} — {quality['feedback']}"
            )

            try:
                binary = load_and_preprocess(sample_path)
                binary, _skew = correct_skew(binary)
            except Exception as e:
                logger.warning(f"Failed to preprocess {sample_path}: {e}")
                continue

            # Global style metrics
            slant = compute_slant_angle(binary)
            all_slants.append(slant)

            stroke_w = compute_stroke_width(binary)
            all_stroke_widths.append(stroke_w)

            # Segment into lines
            lines = segment_lines(binary)
            total_lines += len(lines)

            # Compute line spacing
            for i in range(1, len(lines)):
                gap = lines[i][0] - lines[i - 1][1]
                all_line_spacings.append(float(gap))

            # Process each line
            for line_start, line_end in lines:
                line_img = binary[line_start:line_end, :]
                chars = segment_characters(line_img)

                if len(chars) < 2:
                    continue

                # Extract character metrics & save glyphs
                prev_right_x = 0
                for i, char_img in enumerate(chars):
                    h, w = char_img.shape[:2]
                    all_char_heights.append(float(h))
                    all_char_widths.append(float(w))

                    # Save original glyph
                    resized = resize_char_to_height(char_img, self.target_char_height)
                    glyph_path = glyph_dir / f"glyph_{glyph_index:04d}.png"
                    cv2.imwrite(str(glyph_path), resized)
                    glyph_index += 1

                    # Few-shot augmentation: create variants for richer library
                    augmented = augment_glyph(resized, num_variants=4)
                    for aug_img in augmented:
                        aug_path = glyph_dir / f"glyph_{glyph_index:04d}.png"
                        cv2.imwrite(str(aug_path), aug_img)
                        glyph_index += 1

                    # Estimate spacing (crude: based on width gaps in contours)
                    if i > 0:
                        # We can't get exact x positions from segment_characters
                        # So use a heuristic based on character widths
                        avg_w = np.mean(all_char_widths) if all_char_widths else w
                        spacing = avg_w * 0.3  # Typical inter-char spacing
                        all_spacings.append(spacing)

        # Build profile
        profile = StyleProfile(
            avg_char_height=float(np.mean(all_char_heights)) if all_char_heights else 30.0,
            avg_char_width=float(np.mean(all_char_widths)) if all_char_widths else 20.0,
            char_height_std=float(np.std(all_char_heights)) if all_char_heights else 5.0,
            char_width_std=float(np.std(all_char_widths)) if all_char_widths else 4.0,
            avg_char_spacing=float(np.mean(all_spacings)) if all_spacings else 6.0,
            char_spacing_std=float(np.std(all_spacings)) if all_spacings else 2.0,
            avg_word_spacing=float(np.mean(all_spacings) * 3) if all_spacings else 18.0,
            avg_line_spacing=float(np.mean(all_line_spacings)) if all_line_spacings else 40.0,
            avg_slant_angle=float(np.mean(all_slants)) if all_slants else 0.0,
            slant_angle_std=float(np.std(all_slants)) if all_slants else 2.0,
            avg_stroke_width=float(np.mean(all_stroke_widths)) if all_stroke_widths else 2.0,
            stroke_width_std=float(np.std(all_stroke_widths)) if all_stroke_widths else 0.5,
            total_chars_extracted=glyph_index,
            total_lines_extracted=total_lines,
            glyph_dir=str(glyph_dir),
        )

        # Save profile
        profile.save(output_dir / "style_profile.json")
        logger.info(
            f"Extracted style: {glyph_index} chars, {total_lines} lines, "
            f"slant={profile.avg_slant_angle:.1f}°, stroke={profile.avg_stroke_width:.1f}px"
        )

        return profile
