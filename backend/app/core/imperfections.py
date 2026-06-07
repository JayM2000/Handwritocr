"""Natural imperfections engine for handwriting rendering.

Adds realistic human imperfections to generated handwriting page images
as a post-processing step before PDF compositing:
  - Ink variation (colour shifts, bleed/feathering)
  - Pressure simulation (variable opacity along strokes)
  - Smudge effects (directional blur)
  - Paper interaction (ink absorption halos)
  - Micro-mistakes (ghost strikes, ink blots)
"""

from __future__ import annotations

import logging
import random

import cv2
import numpy as np
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)


class ImperfectionEngine:
    """Applies natural imperfections to handwriting page images."""

    def __init__(
        self,
        ink_variation: float = 0.5,
        pressure_variation: float = 0.5,
        smudge_probability: float = 0.02,
        blot_probability: float = 0.01,
        ghost_probability: float = 0.03,
    ):
        """
        Args:
            ink_variation: Intensity of colour/opacity shifts (0.0–1.0).
            pressure_variation: Intensity of pressure-based opacity changes (0.0–1.0).
            smudge_probability: Chance of smudge per processing region.
            blot_probability: Chance of ink blot near pen-lift points.
            ghost_probability: Chance of ghost re-strike per region.
        """
        self.ink_variation = ink_variation
        self.pressure_variation = pressure_variation
        self.smudge_probability = smudge_probability
        self.blot_probability = blot_probability
        self.ghost_probability = ghost_probability

    def apply(self, page: Image.Image) -> Image.Image:
        """Apply all imperfection effects to a page image.

        Args:
            page: RGBA PIL Image with handwriting on transparent background.

        Returns:
            New RGBA PIL Image with imperfections applied.
        """
        if page.mode != "RGBA":
            page = page.convert("RGBA")

        # Work on a copy
        result = page.copy()

        # Apply effects in order (least to most destructive)
        result = self._apply_ink_variation(result)
        result = self._apply_pressure_simulation(result)
        result = self._apply_ink_bleed(result)
        result = self._apply_ghost_strikes(result)
        result = self._apply_smudges(result)
        result = self._apply_ink_blots(result)

        return result

    def _apply_ink_variation(self, img: Image.Image) -> Image.Image:
        """Shift ink colour slightly per-region for natural inconsistency."""
        if self.ink_variation < 0.01:
            return img

        arr = np.array(img, dtype=np.float32)
        alpha = arr[:, :, 3]

        # Only modify pixels that have ink (alpha > 0)
        ink_mask = alpha > 10

        if not ink_mask.any():
            return img

        # Create a low-frequency noise field for smooth variation
        h, w = arr.shape[:2]
        noise_scale = max(1, min(h, w) // 20)
        noise_r = cv2.resize(
            np.random.randn(noise_scale, noise_scale).astype(np.float32),
            (w, h),
            interpolation=cv2.INTER_LINEAR,
        )
        noise_g = cv2.resize(
            np.random.randn(noise_scale, noise_scale).astype(np.float32),
            (w, h),
            interpolation=cv2.INTER_LINEAR,
        )
        noise_b = cv2.resize(
            np.random.randn(noise_scale, noise_scale).astype(np.float32),
            (w, h),
            interpolation=cv2.INTER_LINEAR,
        )

        intensity = self.ink_variation * 8.0  # Max ±8 colour levels

        for c_idx, noise in enumerate([noise_r, noise_g, noise_b]):
            channel = arr[:, :, c_idx]
            shift = noise * intensity
            channel[ink_mask] = np.clip(channel[ink_mask] + shift[ink_mask], 0, 255)
            arr[:, :, c_idx] = channel

        return Image.fromarray(arr.astype(np.uint8), "RGBA")

    def _apply_pressure_simulation(self, img: Image.Image) -> Image.Image:
        """Vary opacity to simulate pen pressure changes."""
        if self.pressure_variation < 0.01:
            return img

        arr = np.array(img, dtype=np.float32)
        alpha = arr[:, :, 3]
        ink_mask = alpha > 10

        if not ink_mask.any():
            return img

        h, w = arr.shape[:2]

        # Create smooth horizontal pressure wave (simulates hand movement)
        wave_freq = random.uniform(0.002, 0.005)
        phase = random.uniform(0, 2 * np.pi)
        x_coords = np.arange(w, dtype=np.float32)
        pressure_wave = np.sin(x_coords * wave_freq * 2 * np.pi + phase)

        # Add a slower vertical component
        y_coords = np.arange(h, dtype=np.float32)
        vert_wave = np.sin(y_coords * wave_freq * 0.5 * 2 * np.pi + phase * 0.7)

        # Combine into 2D pressure field
        pressure_field = (
            pressure_wave[np.newaxis, :] * 0.7 +
            vert_wave[:, np.newaxis] * 0.3
        )

        # Map to opacity multiplier
        variation = self.pressure_variation * 0.25  # Max ±25% opacity change
        multiplier = 1.0 + pressure_field * variation

        alpha[ink_mask] = np.clip(alpha[ink_mask] * multiplier[ink_mask], 0, 255)
        arr[:, :, 3] = alpha

        return Image.fromarray(arr.astype(np.uint8), "RGBA")

    def _apply_ink_bleed(self, img: Image.Image) -> Image.Image:
        """Simulate ink bleeding into paper fibres (slight edge feathering)."""
        if self.ink_variation < 0.1:
            return img

        # Extract alpha channel and dilate slightly
        arr = np.array(img)
        alpha = arr[:, :, 3].copy()

        if alpha.max() < 10:
            return img

        # Small Gaussian blur on alpha to feather edges
        blur_radius = max(1, int(self.ink_variation * 1.5))
        blurred_alpha = cv2.GaussianBlur(
            alpha.astype(np.float32),
            (blur_radius * 2 + 1, blur_radius * 2 + 1),
            0,
        )

        # Blend: keep strong ink, add light feathered edges
        new_alpha = np.maximum(alpha.astype(np.float32), blurred_alpha * 0.3)
        arr[:, :, 3] = np.clip(new_alpha, 0, 255).astype(np.uint8)

        return Image.fromarray(arr, "RGBA")

    def _apply_ghost_strikes(self, img: Image.Image) -> Image.Image:
        """Add occasional ghost re-strikes (faint shadow offset)."""
        if random.random() > self.ghost_probability * 10:
            return img

        arr = np.array(img)
        alpha = arr[:, :, 3]

        if alpha.max() < 10:
            return img

        h, w = arr.shape[:2]

        # Pick a random horizontal strip to apply ghost effect
        strip_h = max(20, h // 15)
        strip_y = random.randint(0, max(0, h - strip_h))

        strip = arr[strip_y:strip_y + strip_h, :, :].copy()
        strip_alpha = strip[:, :, 3].astype(np.float32)

        if strip_alpha.max() < 10:
            return img

        # Reduce opacity to ~8-12%
        ghost_alpha = (strip_alpha * random.uniform(0.08, 0.12)).astype(np.uint8)

        # Offset by 1–2 pixels
        dx = random.choice([-2, -1, 1, 2])
        dy = random.choice([-1, 0, 1])

        # Create ghost layer
        ghost = strip.copy()
        ghost[:, :, 3] = ghost_alpha

        # Shift and paste
        paste_y = max(0, min(h - strip_h, strip_y + dy))
        paste_x_start = max(0, dx)
        paste_x_end = min(w, w + dx)
        src_x_start = max(0, -dx)
        src_x_end = min(w, w - dx)

        if paste_x_end > paste_x_start and src_x_end > src_x_start:
            src_width = src_x_end - src_x_start
            dst_width = paste_x_end - paste_x_start
            copy_w = min(src_width, dst_width)

            ghost_strip = ghost[:, src_x_start:src_x_start + copy_w, :]
            existing = arr[paste_y:paste_y + strip_h, paste_x_start:paste_x_start + copy_w, :]

            # Alpha composite
            ga = ghost_strip[:, :, 3:4].astype(np.float32) / 255.0
            arr[paste_y:paste_y + strip_h, paste_x_start:paste_x_start + copy_w, :3] = (
                existing[:, :, :3].astype(np.float32) * (1 - ga) +
                ghost_strip[:, :, :3].astype(np.float32) * ga
            ).astype(np.uint8)
            arr[paste_y:paste_y + strip_h, paste_x_start:paste_x_start + copy_w, 3] = np.maximum(
                existing[:, :, 3], ghost_strip[:, :, 3]
            )

        return Image.fromarray(arr, "RGBA")

    def _apply_smudges(self, img: Image.Image) -> Image.Image:
        """Apply occasional directional smudge blur."""
        if random.random() > self.smudge_probability * 5:
            return img

        arr = np.array(img)
        alpha = arr[:, :, 3]

        if alpha.max() < 10:
            return img

        h, w = arr.shape[:2]

        # Find a region with ink
        ink_coords = np.argwhere(alpha > 30)
        if len(ink_coords) < 10:
            return img

        # Pick a random ink region
        idx = random.randint(0, len(ink_coords) - 1)
        cy, cx = ink_coords[idx]

        # Smudge region size
        smudge_w = random.randint(20, 60)
        smudge_h = random.randint(10, 30)

        y1 = max(0, cy - smudge_h // 2)
        y2 = min(h, cy + smudge_h // 2)
        x1 = max(0, cx - smudge_w // 2)
        x2 = min(w, cx + smudge_w // 2)

        if y2 - y1 < 5 or x2 - x1 < 5:
            return img

        region = arr[y1:y2, x1:x2, :].copy()

        # Directional motion blur (horizontal, simulating hand drag)
        kernel_size = random.randint(3, 8)
        kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
        kernel[kernel_size // 2, :] = 1.0 / kernel_size

        for c in range(4):
            region[:, :, c] = cv2.filter2D(region[:, :, c], -1, kernel)

        # Reduce opacity of smudge to make it subtle
        region[:, :, 3] = (region[:, :, 3].astype(np.float32) * 0.6).astype(np.uint8)

        arr[y1:y2, x1:x2, :] = region

        return Image.fromarray(arr, "RGBA")

    def _apply_ink_blots(self, img: Image.Image) -> Image.Image:
        """Add tiny ink blots near ink regions."""
        if random.random() > self.blot_probability * 5:
            return img

        arr = np.array(img)
        alpha = arr[:, :, 3]

        if alpha.max() < 10:
            return img

        h, w = arr.shape[:2]

        # Find ink regions
        ink_coords = np.argwhere(alpha > 50)
        if len(ink_coords) < 5:
            return img

        # Add 1–3 tiny blots
        num_blots = random.randint(1, 3)
        for _ in range(num_blots):
            idx = random.randint(0, len(ink_coords) - 1)
            cy, cx = ink_coords[idx]

            # Offset slightly from ink
            bx = cx + random.randint(-5, 5)
            by = cy + random.randint(-3, 3)

            if 0 <= bx < w and 0 <= by < h:
                # Draw a tiny elliptical blot
                radius_x = random.randint(1, 3)
                radius_y = random.randint(1, 2)
                blot_alpha = random.randint(80, 160)

                for dy in range(-radius_y, radius_y + 1):
                    for dx in range(-radius_x, radius_x + 1):
                        px, py = bx + dx, by + dy
                        if 0 <= px < w and 0 <= py < h:
                            # Elliptical falloff
                            dist = (dx / max(radius_x, 1)) ** 2 + (dy / max(radius_y, 1)) ** 2
                            if dist <= 1.0:
                                falloff = 1.0 - dist
                                a = int(blot_alpha * falloff)
                                # Get ink colour from nearest ink pixel
                                arr[py, px, :3] = arr[cy, cx, :3]
                                arr[py, px, 3] = max(arr[py, px, 3], a)

        return Image.fromarray(arr, "RGBA")


def create_imperfection_engine(
    pen_type: str = "ballpoint",
    intensity: float = 0.5,
) -> ImperfectionEngine:
    """Create an imperfection engine tuned for a specific pen type.

    Args:
        pen_type: One of "ballpoint", "fountain", "gel", "pencil", "felt_tip".
        intensity: Overall intensity multiplier (0.0–1.0).

    Returns:
        Configured ImperfectionEngine.
    """
    # Base settings per pen type
    configs = {
        "ballpoint": {
            "ink_variation": 0.3,
            "pressure_variation": 0.3,
            "smudge_probability": 0.005,
            "blot_probability": 0.005,
            "ghost_probability": 0.01,
        },
        "fountain": {
            "ink_variation": 0.7,
            "pressure_variation": 0.8,
            "smudge_probability": 0.02,
            "blot_probability": 0.03,
            "ghost_probability": 0.02,
        },
        "gel": {
            "ink_variation": 0.2,
            "pressure_variation": 0.15,
            "smudge_probability": 0.008,
            "blot_probability": 0.005,
            "ghost_probability": 0.005,
        },
        "pencil": {
            "ink_variation": 0.5,
            "pressure_variation": 0.7,
            "smudge_probability": 0.04,
            "blot_probability": 0.0,
            "ghost_probability": 0.03,
        },
        "felt_tip": {
            "ink_variation": 0.15,
            "pressure_variation": 0.1,
            "smudge_probability": 0.01,
            "blot_probability": 0.01,
            "ghost_probability": 0.005,
        },
    }

    cfg = configs.get(pen_type, configs["ballpoint"])

    return ImperfectionEngine(
        ink_variation=cfg["ink_variation"] * intensity,
        pressure_variation=cfg["pressure_variation"] * intensity,
        smudge_probability=cfg["smudge_probability"] * intensity,
        blot_probability=cfg["blot_probability"] * intensity,
        ghost_probability=cfg["ghost_probability"] * intensity,
    )
