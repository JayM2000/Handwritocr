"""Pen type profiles for handwriting rendering.

Each pen type defines ink characteristics that affect how generated
handwriting looks — stroke width, colour, opacity, bleed, texture,
and pressure sensitivity.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PenProfile:
    """Defines the visual characteristics of a pen type."""

    name: str
    display_name: str

    # Ink colour (R, G, B)
    color: tuple[int, int, int]

    # Stroke width range (min, max) in pixels at 300 DPI
    stroke_width_min: float
    stroke_width_max: float

    # Opacity range (0–255)
    opacity_min: int
    opacity_max: int

    # Bleed radius (how much ink spreads into paper fibres)
    bleed_radius: float

    # Pressure sensitivity (0.0 = uniform, 1.0 = very responsive)
    pressure_sensitivity: float

    # Texture overlay type
    texture: str  # "none", "grain", "fiber"

    # Whether fast strokes can "skip" (ballpoint behaviour)
    skip_on_fast: bool

    @property
    def stroke_width_range(self) -> tuple[float, float]:
        return (self.stroke_width_min, self.stroke_width_max)

    @property
    def opacity_range(self) -> tuple[int, int]:
        return (self.opacity_min, self.opacity_max)


# ─── Pen Profile Definitions ──────────────────────────────

BALLPOINT = PenProfile(
    name="ballpoint",
    display_name="Ballpoint",
    color=(15, 15, 80),          # Dark blue-black
    stroke_width_min=1.8,
    stroke_width_max=2.8,
    opacity_min=200,
    opacity_max=240,
    bleed_radius=0.0,
    pressure_sensitivity=0.3,
    texture="none",
    skip_on_fast=True,
)

FOUNTAIN = PenProfile(
    name="fountain",
    display_name="Fountain Pen",
    color=(10, 10, 45),          # Deep ink blue-black
    stroke_width_min=1.5,
    stroke_width_max=4.5,
    opacity_min=180,
    opacity_max=250,
    bleed_radius=1.2,
    pressure_sensitivity=0.85,
    texture="fiber",
    skip_on_fast=False,
)

GEL = PenProfile(
    name="gel",
    display_name="Gel Pen",
    color=(20, 20, 60),          # Vibrant dark blue
    stroke_width_min=2.2,
    stroke_width_max=3.0,
    opacity_min=220,
    opacity_max=245,
    bleed_radius=0.3,
    pressure_sensitivity=0.15,
    texture="none",
    skip_on_fast=False,
)

PENCIL = PenProfile(
    name="pencil",
    display_name="Pencil",
    color=(60, 60, 60),          # Graphite grey
    stroke_width_min=1.5,
    stroke_width_max=3.5,
    opacity_min=100,
    opacity_max=190,
    bleed_radius=0.0,
    pressure_sensitivity=0.7,
    texture="grain",
    skip_on_fast=False,
)

FELT_TIP = PenProfile(
    name="felt_tip",
    display_name="Felt-Tip",
    color=(25, 25, 25),          # Rich black
    stroke_width_min=3.0,
    stroke_width_max=4.0,
    opacity_min=230,
    opacity_max=250,
    bleed_radius=0.5,
    pressure_sensitivity=0.1,
    texture="none",
    skip_on_fast=False,
)


# ─── Registry ─────────────────────────────────────────────

PEN_PROFILES: dict[str, PenProfile] = {
    "ballpoint": BALLPOINT,
    "fountain": FOUNTAIN,
    "gel": GEL,
    "pencil": PENCIL,
    "felt_tip": FELT_TIP,
}


def get_pen_profile(pen_type: str) -> PenProfile:
    """Get a pen profile by name, defaulting to ballpoint."""
    return PEN_PROFILES.get(pen_type, BALLPOINT)
