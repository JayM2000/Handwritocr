"""Low-level image processing utilities using OpenCV and Pillow.

All heavy image operations (preprocessing, segmentation, contour analysis)
are centralised here so the rest of the codebase stays clean.
"""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


# ─── Preprocessing ──────────────────────────────────────
def load_and_preprocess(image_path: str) -> np.ndarray:
    """Load an image and preprocess for handwriting analysis.

    Returns a clean binary image (white text on black background).
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    # Denoise
    img = cv2.fastNlMeansDenoising(img, h=10)

    # Adaptive threshold — handles uneven lighting
    binary = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10
    )

    # Morphological cleanup — remove tiny specks
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    return binary


def correct_skew(binary: np.ndarray, max_angle: float = 15.0) -> tuple[np.ndarray, float]:
    """Detect and correct page skew.

    Returns the deskewed image and the detected angle.
    """
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) < 50:
        return binary, 0.0

    # Minimum area rectangle gives us the skew angle
    angle = cv2.minAreaRect(coords)[-1]

    # Normalise angle
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Clamp to reasonable range
    if abs(angle) > max_angle:
        return binary, 0.0

    h, w = binary.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        binary, M, (w, h), flags=cv2.INTER_CUBIC, borderValue=0
    )
    return rotated, angle


# ─── Segmentation ───────────────────────────────────────
def segment_lines(binary: np.ndarray, min_gap: int = 8) -> list[tuple[int, int]]:
    """Segment text lines using horizontal projection.

    Returns list of (y_start, y_end) tuples for each line.
    """
    h_proj = np.sum(binary, axis=1)
    threshold = np.max(h_proj) * 0.02

    in_line = False
    lines: list[tuple[int, int]] = []
    start = 0

    for y, val in enumerate(h_proj):
        if val > threshold and not in_line:
            start = y
            in_line = True
        elif val <= threshold and in_line:
            if y - start > min_gap:
                lines.append((start, y))
            in_line = False

    if in_line:
        lines.append((start, len(h_proj) - 1))

    return lines


def segment_characters(
    line_img: np.ndarray, min_width: int = 4, min_height: int = 8
) -> list[np.ndarray]:
    """Extract individual characters from a text line using connected components.

    Returns list of character images (cropped, normalised).
    """
    contours, _ = cv2.findContours(
        line_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    char_imgs: list[tuple[int, np.ndarray]] = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w < min_width or h < min_height:
            continue
        char_crop = line_img[y : y + h, x : x + w]
        char_imgs.append((x, char_crop))

    # Sort left-to-right
    char_imgs.sort(key=lambda c: c[0])
    return [img for _, img in char_imgs]


# ─── Feature Extraction ────────────────────────────────
def compute_stroke_width(binary: np.ndarray) -> float:
    """Estimate average stroke width using distance transform."""
    dist = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    stroke_pixels = dist[binary > 0]
    if len(stroke_pixels) == 0:
        return 2.0
    return float(np.mean(stroke_pixels) * 2)


def compute_slant_angle(binary: np.ndarray) -> float:
    """Estimate the slant angle of handwriting in degrees.

    Positive = right slant, Negative = left slant.
    """
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) < 20:
        return 0.0

    # Use PCA to find principal direction
    mean = np.mean(coords, axis=0)
    centered = coords - mean
    cov = np.cov(centered.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Angle of the dominant eigenvector
    angle = np.degrees(np.arctan2(eigenvectors[0, 1], eigenvectors[1, 1]))
    return float(angle)


def resize_char_to_height(char_img: np.ndarray, target_height: int) -> np.ndarray:
    """Resize a character image to a target height, preserving aspect ratio."""
    h, w = char_img.shape[:2]
    if h == 0:
        return char_img
    scale = target_height / h
    new_w = max(1, int(w * scale))
    return cv2.resize(char_img, (new_w, target_height), interpolation=cv2.INTER_AREA)


def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV numpy array."""
    return np.array(pil_img.convert("L"))


def cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
    """Convert OpenCV numpy array to PIL Image."""
    return Image.fromarray(cv2_img)


# ─── Quality Scoring ───────────────────────────────────
def score_image_quality(image_path: str) -> dict:
    """Assess the quality of a handwriting sample image.

    Returns a dict with:
        - sharpness: float (0–1), higher is sharper
        - contrast: float (0–1), higher is better contrast
        - coverage: float (0–1), fraction of image with ink
        - overall: float (0–1), weighted composite score
        - usable: bool, whether the sample is good enough
        - feedback: str, human-readable feedback message
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {
            "sharpness": 0.0,
            "contrast": 0.0,
            "coverage": 0.0,
            "overall": 0.0,
            "usable": False,
            "feedback": "Cannot read image file",
        }

    h, w = img.shape

    # Sharpness via Laplacian variance (normalised to 0–1)
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    sharpness_raw = laplacian.var()
    sharpness = min(1.0, sharpness_raw / 500.0)  # 500 is "very sharp"

    # Contrast via standard deviation of pixel intensities
    contrast = min(1.0, float(np.std(img)) / 80.0)

    # Coverage: fraction of pixels that are "ink" (dark after threshold)
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coverage = float(np.sum(binary > 0)) / (h * w)
    # Ideal coverage is 5–40%; too little = empty, too much = solid
    if coverage < 0.01:
        coverage_score = 0.0
    elif coverage < 0.05:
        coverage_score = coverage / 0.05  # Ramp up to 1.0
    elif coverage <= 0.45:
        coverage_score = 1.0
    else:
        coverage_score = max(0.0, 1.0 - (coverage - 0.45) / 0.3)

    # Weighted composite
    overall = sharpness * 0.35 + contrast * 0.30 + coverage_score * 0.35
    usable = overall >= 0.25

    # Feedback
    issues = []
    if sharpness < 0.2:
        issues.append("image is blurry")
    if contrast < 0.2:
        issues.append("low contrast (ink too light)")
    if coverage < 0.02:
        issues.append("too little text visible")
    if coverage > 0.5:
        issues.append("image is too dark or solid")

    if issues:
        feedback = "Issues: " + ", ".join(issues) + "."
    elif overall > 0.7:
        feedback = "Excellent sample quality!"
    elif overall > 0.4:
        feedback = "Good sample quality."
    else:
        feedback = "Acceptable but could be clearer."

    return {
        "sharpness": round(sharpness, 3),
        "contrast": round(contrast, 3),
        "coverage": round(coverage_score, 3),
        "overall": round(overall, 3),
        "usable": usable,
        "feedback": feedback,
    }


def augment_glyph(
    glyph: np.ndarray,
    num_variants: int = 4,
) -> list[np.ndarray]:
    """Create augmented variants of a glyph for richer style library.

    Generates slight variations via rotation, scaling, and noise to
    simulate natural character variation from fewer samples.

    Args:
        glyph: Grayscale glyph image.
        num_variants: Number of augmented copies to produce.

    Returns:
        List of augmented glyph images (does NOT include the original).
    """
    import random

    variants = []
    h, w = glyph.shape[:2]

    for _ in range(num_variants):
        aug = glyph.copy()

        # Random slight rotation (±3°)
        angle = random.gauss(0, 1.5)
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        aug = cv2.warpAffine(aug, M, (w, h), borderValue=0)

        # Random scale (±5%)
        scale = random.gauss(1.0, 0.03)
        if abs(scale - 1.0) > 0.005:
            new_w = max(3, int(w * scale))
            new_h = max(3, int(h * scale))
            aug = cv2.resize(aug, (new_w, new_h), interpolation=cv2.INTER_AREA)
            # Pad or crop back to original size
            if new_h > h or new_w > w:
                aug = aug[:h, :w]
            elif new_h < h or new_w < w:
                padded = np.zeros((h, w), dtype=np.uint8)
                ph = min(new_h, h)
                pw = min(new_w, w)
                padded[:ph, :pw] = aug[:ph, :pw]
                aug = padded

        # Random noise (salt-and-pepper, very light)
        noise_mask = np.random.random(aug.shape) < 0.01
        aug[noise_mask] = np.where(
            aug[noise_mask] > 127,
            np.clip(aug[noise_mask].astype(int) - 30, 0, 255).astype(np.uint8),
            np.clip(aug[noise_mask].astype(int) + 30, 0, 255).astype(np.uint8),
        )

        # Random slight horizontal shear (slant variation)
        shear = random.gauss(0, 0.02)
        if abs(shear) > 0.005:
            S = np.float32([[1, shear, 0], [0, 1, 0]])
            aug = cv2.warpAffine(aug, S, (w, h), borderValue=0)

        variants.append(aug)

    return variants

