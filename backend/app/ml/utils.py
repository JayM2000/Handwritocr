"""Utility functions for handwriting synthesis ML pipeline.

Provides:
  - Character alphabet and encoding
  - Stroke normalization / denormalization
  - Sequence padding helpers
"""

from __future__ import annotations

import numpy as np

# ─── Alphabet ───────────────────────────────────────────
# Characters supported by the model. Index 0 is reserved for padding/unknown.
CHARS = (
    " !\"#$%&'()*+,-./0123456789:;<=>?@"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
    "abcdefghijklmnopqrstuvwxyz{|}~"
)
CHAR_TO_IDX: dict[str, int] = {c: i + 1 for i, c in enumerate(CHARS)}
IDX_TO_CHAR: dict[int, str] = {i + 1: c for i, c in enumerate(CHARS)}
VOCAB_SIZE = len(CHARS) + 1  # +1 for padding index 0


def text_to_indices(text: str) -> list[int]:
    """Convert a text string to a list of character indices."""
    return [CHAR_TO_IDX.get(c, 0) for c in text]


def indices_to_text(indices: list[int]) -> str:
    """Convert character indices back to text."""
    return "".join(IDX_TO_CHAR.get(i, "") for i in indices)


def text_to_one_hot(text: str) -> np.ndarray:
    """Convert text to one-hot encoded matrix.

    Returns:
        Array of shape (len(text), VOCAB_SIZE).
    """
    indices = text_to_indices(text)
    one_hot = np.zeros((len(indices), VOCAB_SIZE), dtype=np.float32)
    for i, idx in enumerate(indices):
        one_hot[i, idx] = 1.0
    return one_hot


# ─── Stroke Normalization ──────────────────────────────
def normalize_strokes(
    strokes: np.ndarray,
    scale_factor: float | None = None,
) -> tuple[np.ndarray, float, float, float]:
    """Normalize stroke data to zero mean, unit variance.

    Args:
        strokes: Array of shape (N, 3) — columns are (dx, dy, pen_up).
        scale_factor: If provided, use this instead of computing from data.

    Returns:
        Tuple of (normalized_strokes, mean_x, mean_y, std).
    """
    data = strokes.copy().astype(np.float32)
    offsets = data[:, :2]

    mean_x = float(np.mean(offsets[:, 0]))
    mean_y = float(np.mean(offsets[:, 1]))

    offsets[:, 0] -= mean_x
    offsets[:, 1] -= mean_y

    if scale_factor is None:
        std = float(np.std(offsets))
        if std < 1e-6:
            std = 1.0
    else:
        std = scale_factor

    offsets /= std
    data[:, :2] = offsets

    return data, mean_x, mean_y, std


def denormalize_strokes(
    strokes: np.ndarray,
    mean_x: float,
    mean_y: float,
    std: float,
) -> np.ndarray:
    """Reverse normalization of strokes."""
    data = strokes.copy().astype(np.float32)
    data[:, 0] = data[:, 0] * std + mean_x
    data[:, 1] = data[:, 1] * std + mean_y
    return data


def strokes_to_points(strokes: np.ndarray) -> list[list[tuple[float, float]]]:
    """Convert stroke offsets (dx, dy, pen_up) to absolute point sequences.

    Returns list of strokes, where each stroke is a list of (x, y) points.
    """
    x, y = 0.0, 0.0
    current_stroke: list[tuple[float, float]] = []
    all_strokes: list[list[tuple[float, float]]] = []

    for dx, dy, pen_up in strokes:
        x += float(dx)
        y += float(dy)
        current_stroke.append((x, y))

        if pen_up > 0.5:
            if current_stroke:
                all_strokes.append(current_stroke)
            current_stroke = []

    if current_stroke:
        all_strokes.append(current_stroke)

    return all_strokes


# ─── Padding Helpers ───────────────────────────────────
def pad_stroke_sequence(
    strokes: np.ndarray, max_len: int
) -> tuple[np.ndarray, int]:
    """Pad stroke sequence to max_len.

    Returns (padded_array, original_length).
    """
    orig_len = len(strokes)
    if orig_len >= max_len:
        return strokes[:max_len], max_len

    padding = np.zeros((max_len - orig_len, strokes.shape[1]), dtype=np.float32)
    # Mark padding as pen-up
    padding[:, 2] = 1.0
    padded = np.concatenate([strokes, padding], axis=0)
    return padded, orig_len


def pad_text_sequence(
    indices: list[int], max_len: int
) -> tuple[list[int], int]:
    """Pad text index sequence to max_len."""
    orig_len = len(indices)
    if orig_len >= max_len:
        return indices[:max_len], max_len
    padded = indices + [0] * (max_len - orig_len)
    return padded, orig_len
