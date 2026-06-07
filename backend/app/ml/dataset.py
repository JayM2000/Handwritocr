"""IAM On-Line Handwriting Dataset loader.

Handles loading and preprocessing of the IAM-OnDB dataset:
  - Parses XML stroke files → (dx, dy, pen_up) sequences
  - Pairs with text transcriptions
  - Provides PyTorch Dataset + DataLoader utilities
"""

from __future__ import annotations

import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from .utils import (
    text_to_indices,
    normalize_strokes,
    pad_stroke_sequence,
    pad_text_sequence,
    VOCAB_SIZE,
)

logger = logging.getLogger(__name__)


# ─── IAM XML Parser ───────────────────────────────────
def parse_iam_stroke_xml(xml_path: str) -> list[np.ndarray] | None:
    """Parse an IAM Online stroke XML file.

    Returns list of strokes, each a numpy array of (x, y, timestamp).
    Returns None if parsing fails.
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError):
        return None

    strokes = []
    for stroke_elem in root.iter("Stroke"):
        points = []
        for point in stroke_elem.iter("Point"):
            x = float(point.get("x", 0))
            y = float(point.get("y", 0))
            t = float(point.get("time", 0))
            points.append([x, y, t])
        if points:
            strokes.append(np.array(points, dtype=np.float32))

    return strokes if strokes else None


def raw_strokes_to_offsets(strokes: list[np.ndarray]) -> np.ndarray:
    """Convert absolute stroke points to offset format (dx, dy, pen_up).

    Args:
        strokes: List of stroke arrays, each (N, 3) with (x, y, t).

    Returns:
        Array of shape (total_points, 3) with (dx, dy, pen_up).
    """
    offsets = []

    for i, stroke in enumerate(strokes):
        coords = stroke[:, :2]  # (x, y)

        # Compute deltas
        if len(coords) < 2:
            continue

        dx = np.diff(coords[:, 0])
        dy = np.diff(coords[:, 1])

        # pen_up = 0 for all points except last in each stroke
        pen_up = np.zeros(len(dx), dtype=np.float32)
        pen_up[-1] = 1.0  # Pen lifts at end of stroke

        stroke_offsets = np.column_stack([dx, dy, pen_up])
        offsets.append(stroke_offsets)

    if not offsets:
        return np.zeros((1, 3), dtype=np.float32)

    return np.concatenate(offsets, axis=0).astype(np.float32)


# ─── Dataset ──────────────────────────────────────────
class IAMDataset(Dataset):
    """PyTorch dataset for IAM On-Line Handwriting Database.

    Expected directory structure:
        data_dir/
            lineStrokes/        # XML stroke files
            ascii/              # Text transcription files
    """

    def __init__(
        self,
        data_dir: str,
        max_stroke_len: int = 700,
        max_text_len: int = 75,
        normalize: bool = True,
        scale_factor: float | None = None,
    ):
        self.data_dir = Path(data_dir)
        self.max_stroke_len = max_stroke_len
        self.max_text_len = max_text_len
        self.normalize = normalize
        self.scale_factor = scale_factor

        self.samples: list[tuple[str, str]] = []  # (stroke_xml_path, text)
        self._load_samples()

        logger.info(f"IAMDataset: {len(self.samples)} samples loaded from {data_dir}")

    def _load_samples(self) -> None:
        """Scan the data directory and pair stroke XMLs with transcriptions."""
        stroke_dir = self.data_dir / "lineStrokes"
        ascii_dir = self.data_dir / "ascii"

        if not stroke_dir.exists():
            logger.warning(f"Stroke directory not found: {stroke_dir}")
            return

        # Parse transcription files
        transcriptions: dict[str, str] = {}
        if ascii_dir.exists():
            for txt_file in ascii_dir.rglob("*.txt"):
                try:
                    lines = txt_file.read_text(errors="ignore").splitlines()
                    # IAM format: skip header lines starting with #
                    csr_flag = False
                    for line in lines:
                        if line.startswith("CSR"):
                            csr_flag = True
                            continue
                        if csr_flag and line.strip():
                            # Format: line-id ok/err gray components text...
                            parts = line.strip().split()
                            if len(parts) >= 9:
                                line_id = parts[0]
                                text = " ".join(parts[8:])
                                transcriptions[line_id] = text
                except Exception:
                    continue

        # Match stroke XMLs with transcriptions
        for xml_file in sorted(stroke_dir.rglob("*.xml")):
            line_id = xml_file.stem
            text = transcriptions.get(line_id, "")
            if text and len(text) <= self.max_text_len:
                self.samples.append((str(xml_file), text))

        # If no transcriptions found, just load strokes without text
        if not self.samples:
            for xml_file in sorted(stroke_dir.rglob("*.xml")):
                self.samples.append((str(xml_file), "the quick brown fox"))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        xml_path, text = self.samples[idx]

        # Parse strokes
        raw_strokes = parse_iam_stroke_xml(xml_path)
        if raw_strokes is None:
            # Return dummy data
            return self._dummy_sample()

        offsets = raw_strokes_to_offsets(raw_strokes)

        # Normalize
        if self.normalize:
            offsets, _, _, _ = normalize_strokes(offsets, self.scale_factor)

        # Pad strokes
        stroke_padded, stroke_len = pad_stroke_sequence(offsets, self.max_stroke_len)

        # Encode text
        text_indices = text_to_indices(text)
        text_padded, text_len = pad_text_sequence(text_indices, self.max_text_len)

        # One-hot encode text
        text_onehot = np.zeros((self.max_text_len, VOCAB_SIZE), dtype=np.float32)
        for i, idx_val in enumerate(text_padded):
            if i < len(text_padded):
                text_onehot[i, idx_val] = 1.0

        return {
            "strokes": torch.from_numpy(stroke_padded),
            "stroke_len": torch.tensor(stroke_len, dtype=torch.long),
            "text_onehot": torch.from_numpy(text_onehot),
            "text_len": torch.tensor(text_len, dtype=torch.long),
            "text_indices": torch.tensor(text_padded, dtype=torch.long),
        }

    def _dummy_sample(self) -> dict[str, torch.Tensor]:
        """Return a dummy sample for error cases."""
        return {
            "strokes": torch.zeros(self.max_stroke_len, 3),
            "stroke_len": torch.tensor(1, dtype=torch.long),
            "text_onehot": torch.zeros(self.max_text_len, VOCAB_SIZE),
            "text_len": torch.tensor(1, dtype=torch.long),
            "text_indices": torch.zeros(self.max_text_len, dtype=torch.long),
        }


# ─── Synthetic Dataset (for testing without IAM) ─────
class SyntheticStrokeDataset(Dataset):
    """Generates synthetic stroke data for testing the model pipeline.

    Creates simple line/curve strokes paired with dummy text.
    """

    def __init__(
        self,
        num_samples: int = 1000,
        max_stroke_len: int = 300,
        max_text_len: int = 50,
    ):
        self.num_samples = num_samples
        self.max_stroke_len = max_stroke_len
        self.max_text_len = max_text_len

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        rng = np.random.RandomState(idx)

        # Generate random stroke offsets
        stroke_len = rng.randint(50, self.max_stroke_len)
        dx = rng.randn(stroke_len).astype(np.float32) * 0.5
        dy = rng.randn(stroke_len).astype(np.float32) * 0.3
        pen_up = np.zeros(stroke_len, dtype=np.float32)
        # Random pen lifts
        for i in range(0, stroke_len, rng.randint(5, 20)):
            pen_up[min(i, stroke_len - 1)] = 1.0

        strokes = np.column_stack([dx, dy, pen_up])
        strokes_padded, s_len = pad_stroke_sequence(strokes, self.max_stroke_len)

        # Random text
        text = "hello world test"[:rng.randint(5, 16)]
        text_indices = text_to_indices(text)
        text_padded, t_len = pad_text_sequence(text_indices, self.max_text_len)

        text_onehot = np.zeros((self.max_text_len, VOCAB_SIZE), dtype=np.float32)
        for i, v in enumerate(text_padded):
            text_onehot[i, v] = 1.0

        return {
            "strokes": torch.from_numpy(strokes_padded),
            "stroke_len": torch.tensor(s_len, dtype=torch.long),
            "text_onehot": torch.from_numpy(text_onehot),
            "text_len": torch.tensor(t_len, dtype=torch.long),
            "text_indices": torch.tensor(text_padded, dtype=torch.long),
        }


# ─── DataLoader Factory ──────────────────────────────
def create_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 0,
) -> DataLoader:
    """Create a DataLoader with appropriate settings."""
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=True,
    )
