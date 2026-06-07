"""User-specific fine-tuning of the handwriting model.

Takes a pre-trained model and fine-tunes it on user's handwriting samples.
Process:
  1. Extract strokes from user's sample images (via skeletonization)
  2. Freeze early LSTM layers
  3. Fine-tune last LSTM layer + MDN head with low learning rate
  4. Save user-specific checkpoint
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.optim as optim

from .model import HandwritingModel, mdn_loss
from .utils import (
    normalize_strokes,
    pad_stroke_sequence,
    text_to_one_hot,
    VOCAB_SIZE,
)

logger = logging.getLogger(__name__)


# ─── Stroke Extraction from Images ────────────────────
def extract_strokes_from_image(
    image_path: str, simplify: bool = True
) -> np.ndarray | None:
    """Extract approximate stroke data from a handwriting image.

    Uses morphological skeletonization → contour tracing to approximate
    pen strokes from a binary image.

    Args:
        image_path: Path to the handwriting sample image.
        simplify: If True, simplify the contour (fewer points).

    Returns:
        Array of shape (N, 3) with (dx, dy, pen_up), or None if fails.
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None

        # Preprocess
        img = cv2.fastNlMeansDenoising(img, h=10)
        binary = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 21, 10
        )

        # Skeletonize using morphological thinning
        skeleton = cv2.ximgproc.thinning(binary) if hasattr(cv2, "ximgproc") else _simple_skeleton(binary)

        # Find contours on skeleton
        contours, _ = cv2.findContours(
            skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return None

        # Sort contours left-to-right
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

        # Convert contours to stroke offsets
        all_offsets = []
        for contour in contours:
            if len(contour) < 3:
                continue

            points = contour.squeeze()
            if points.ndim != 2:
                continue

            if simplify:
                # Simplify contour
                epsilon = 0.5 * cv2.arcLength(contour, False)
                approx = cv2.approxPolyDP(contour, epsilon * 0.01, False)
                points = approx.squeeze()
                if points.ndim != 2 or len(points) < 2:
                    continue

            # Compute offsets
            dx = np.diff(points[:, 0]).astype(np.float32)
            dy = np.diff(points[:, 1]).astype(np.float32)
            pen_up = np.zeros(len(dx), dtype=np.float32)
            pen_up[-1] = 1.0  # Pen up at end of stroke

            offsets = np.column_stack([dx, dy, pen_up])
            all_offsets.append(offsets)

        if not all_offsets:
            return None

        return np.concatenate(all_offsets, axis=0)

    except Exception as e:
        logger.warning(f"Stroke extraction failed for {image_path}: {e}")
        return None


def _simple_skeleton(binary: np.ndarray) -> np.ndarray:
    """Simple skeletonization fallback when cv2.ximgproc is unavailable."""
    skeleton = np.zeros_like(binary)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    temp = binary.copy()

    while True:
        eroded = cv2.erode(temp, element)
        dilated = cv2.dilate(eroded, element)
        diff = cv2.subtract(temp, dilated)
        skeleton = cv2.bitwise_or(skeleton, diff)
        temp = eroded.copy()
        if cv2.countNonZero(temp) == 0:
            break

    return skeleton


# ─── Fine-tuner ───────────────────────────────────────
class FineTuner:
    """Fine-tune a pre-trained model on user's handwriting samples."""

    def __init__(
        self,
        base_checkpoint: str | Path,
        device: str | None = None,
    ):
        self.device = torch.device(
            device or ("cuda" if torch.cuda.is_available() else "cpu")
        )

        # Load base model
        self.model = HandwritingModel()
        self.model.to(self.device)

        ckpt = torch.load(base_checkpoint, map_location=self.device, weights_only=False)
        if "model_state_dict" in ckpt:
            self.model.load_state_dict(ckpt["model_state_dict"])
        else:
            self.model.load_state_dict(ckpt)

        logger.info(f"Base model loaded from {base_checkpoint}")

        # Freeze early layers (LSTM 1 + window)
        for param in self.model.lstm1.parameters():
            param.requires_grad = False
        for param in self.model.window.parameters():
            param.requires_grad = False

        # Only train: LSTM 2, LSTM 3, MDN head
        trainable = sum(
            p.numel() for p in self.model.parameters() if p.requires_grad
        )
        total = sum(p.numel() for p in self.model.parameters())
        logger.info(f"Fine-tuning {trainable:,} / {total:,} parameters")

    def fine_tune(
        self,
        sample_image_paths: list[str],
        sample_text: str = "the quick brown fox jumps over the lazy dog",
        num_iterations: int = 100,
        learning_rate: float = 1e-5,
        output_checkpoint: str | Path = "user_model.pt",
    ) -> Path:
        """Fine-tune the model on user's handwriting samples.

        Args:
            sample_image_paths: Paths to user's handwriting sample images.
            sample_text: Representative text (for pairing with strokes).
            num_iterations: Number of fine-tuning iterations.
            learning_rate: Learning rate (should be low).
            output_checkpoint: Where to save the fine-tuned model.

        Returns:
            Path to the saved checkpoint.
        """
        # Extract strokes from all samples
        all_strokes = []
        for path in sample_image_paths:
            strokes = extract_strokes_from_image(path)
            if strokes is not None and len(strokes) > 10:
                all_strokes.append(strokes)

        if not all_strokes:
            logger.warning("No valid strokes extracted — skipping fine-tuning")
            # Save the base model as-is
            output_path = Path(output_checkpoint)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save({"model_state_dict": self.model.state_dict()}, output_path)
            return output_path

        logger.info(f"Extracted strokes from {len(all_strokes)} samples")

        # Prepare training data
        text_onehot = text_to_one_hot(sample_text)
        text_tensor = (
            torch.from_numpy(text_onehot).unsqueeze(0).to(self.device)
        )

        # Optimizer (low LR for fine-tuning)
        optimizer = optim.Adam(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=learning_rate,
        )

        self.model.train()

        for iteration in range(num_iterations):
            total_loss = 0.0

            for strokes in all_strokes:
                # Normalize
                strokes_norm, _, _, _ = normalize_strokes(strokes)
                max_len = min(len(strokes_norm), 500)
                strokes_padded, _ = pad_stroke_sequence(strokes_norm, max_len)

                stroke_tensor = (
                    torch.from_numpy(strokes_padded).unsqueeze(0).to(self.device)
                )

                # Forward
                input_strokes = stroke_tensor[:, :-1, :]
                target_strokes = stroke_tensor[:, 1:, :]

                optimizer.zero_grad()
                mdn_list, _, _ = self.model(input_strokes, text_tensor)

                loss = torch.tensor(0.0, device=self.device)
                seq_len = target_strokes.size(1)
                for t in range(min(seq_len, len(mdn_list))):
                    loss += mdn_loss(mdn_list[t], target_strokes[:, t, :])
                loss = loss / seq_len

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 5.0)
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(all_strokes)
            if (iteration + 1) % 20 == 0:
                logger.info(
                    f"Fine-tune iter {iteration + 1}/{num_iterations} | loss={avg_loss:.4f}"
                )

        # Save fine-tuned model
        output_path = Path(output_checkpoint)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"model_state_dict": self.model.state_dict()}, output_path)
        logger.info(f"Fine-tuned model saved: {output_path}")

        return output_path
