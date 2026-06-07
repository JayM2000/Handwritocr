"""Inference engine for handwriting generation.

Takes input text and generates stroke sequences using a trained model.
Supports:
  - Temperature/bias control for randomness
  - Style priming from user stroke data
  - Cached model loading for fast repeated inference
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import torch

from .model import HandwritingModel, MDNParams
from .utils import text_to_one_hot, VOCAB_SIZE

logger = logging.getLogger(__name__)


class HandwritingInference:
    """Generate handwriting strokes from text using a trained model."""

    def __init__(
        self,
        checkpoint_path: str | Path | None = None,
        device: str | None = None,
        hidden_size: int = 400,
        num_mixtures: int = 20,
        num_attn_mixtures: int = 10,
    ):
        self.device = torch.device(
            device or ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.hidden_size = hidden_size
        self.num_mixtures = num_mixtures

        # Build model
        self.model = HandwritingModel(
            hidden_size=hidden_size,
            num_mixtures=num_mixtures,
            num_attn_mixtures=num_attn_mixtures,
        )
        self.model.to(self.device)
        self.model.eval()

        # Load checkpoint if provided
        if checkpoint_path and Path(checkpoint_path).exists():
            self._load_checkpoint(checkpoint_path)
            logger.info(f"Model loaded from {checkpoint_path}")
        else:
            logger.warning("No checkpoint loaded — model will produce random output")

    def _load_checkpoint(self, path: str | Path) -> None:
        """Load model weights from checkpoint."""
        ckpt = torch.load(path, map_location=self.device, weights_only=False)
        if "model_state_dict" in ckpt:
            self.model.load_state_dict(ckpt["model_state_dict"])
        else:
            self.model.load_state_dict(ckpt)

    @torch.no_grad()
    def generate(
        self,
        text: str,
        bias: float = 1.0,
        max_steps: int = 2000,
        prime_strokes: np.ndarray | None = None,
        prime_steps: int = 0,
    ) -> np.ndarray:
        """Generate handwriting strokes for given text.

        Args:
            text: Input text to generate handwriting for.
            bias: Controls randomness. 0 = max random, >1 = more consistent.
            max_steps: Maximum number of stroke points to generate.
            prime_strokes: Optional stroke data to prime the model with (for style).
            prime_steps: Number of priming steps to use.

        Returns:
            Array of shape (N, 3) with (dx, dy, pen_up) stroke data.
        """
        # Encode text
        text_onehot = text_to_one_hot(text)
        text_tensor = torch.from_numpy(text_onehot).unsqueeze(0).to(self.device)

        # Initial state
        state = self.model.get_initial_state(1, self.device)

        # Starting stroke point
        x = torch.zeros(1, 3, device=self.device)

        # Priming phase (feed existing strokes to capture style)
        if prime_strokes is not None and prime_steps > 0:
            prime_data = torch.from_numpy(prime_strokes[:prime_steps]).float()
            prime_data = prime_data.unsqueeze(0).to(self.device)
            for t in range(min(prime_steps, prime_data.size(1))):
                x_prime = prime_data[:, t, :]
                _, state, _ = self.model.forward_step(x_prime, text_tensor, state)

        # Generation phase
        strokes = []
        for step in range(max_steps):
            mdn_params, state, phi = self.model.forward_step(x, text_tensor, state)

            # Sample from MDN with bias
            dx, dy, pen_up = self._sample_mdn(mdn_params, bias)
            strokes.append([dx, dy, pen_up])

            # Prepare next input
            x = torch.tensor([[dx, dy, pen_up]], device=self.device, dtype=torch.float32)

            # Check if attention has passed the end of the text
            if phi is not None:
                phi_np = phi[0].cpu().numpy()
                if np.argmax(phi_np) >= len(text) - 1 and pen_up > 0.5:
                    break

            # Early stop on end of stroke
            if pen_up > 0.9 and step > len(text) * 15:
                break

        return np.array(strokes, dtype=np.float32)

    def _sample_mdn(
        self, params: MDNParams, bias: float = 1.0
    ) -> tuple[float, float, float]:
        """Sample a point from the MDN output.

        Args:
            params: MDN parameters.
            bias: Temperature bias. Higher = less random.

        Returns:
            (dx, dy, pen_up) sampled point.
        """
        pi = params.pi[0].cpu().numpy()
        mu_x = params.mu_x[0].cpu().numpy()
        mu_y = params.mu_y[0].cpu().numpy()
        sigma_x = params.sigma_x[0].cpu().numpy()
        sigma_y = params.sigma_y[0].cpu().numpy()
        rho = params.rho[0].cpu().numpy()
        eos = params.eos[0, 0].cpu().item()

        # Apply bias to mixture weights (sharpen distribution)
        if bias > 0:
            pi = np.log(pi + 1e-8) * (1 + bias)
            pi = np.exp(pi) / np.sum(np.exp(pi))

        # Choose mixture component
        idx = np.random.choice(len(pi), p=pi)

        # Sample from chosen bivariate Gaussian
        mean = [mu_x[idx], mu_y[idx]]
        sx = sigma_x[idx] / (1 + bias) if bias > 0 else sigma_x[idx]
        sy = sigma_y[idx] / (1 + bias) if bias > 0 else sigma_y[idx]
        r = rho[idx]

        # Covariance matrix
        cov = [[sx * sx, r * sx * sy], [r * sx * sy, sy * sy]]

        try:
            sample = np.random.multivariate_normal(mean, cov)
        except np.linalg.LinAlgError:
            sample = np.array(mean)

        dx = float(sample[0])
        dy = float(sample[1])

        # Pen up/down
        pen_up = 1.0 if np.random.random() < eos else 0.0

        return dx, dy, pen_up

    def is_loaded(self) -> bool:
        """Check if model has loaded weights (not random)."""
        checkpoint_dir = Path(__file__).parent / "checkpoints"
        return any(checkpoint_dir.glob("*.pt"))


# ─── Singleton / Cache ────────────────────────────────
_inference_cache: dict[str, HandwritingInference] = {}


def get_inference_engine(
    checkpoint_path: str | Path | None = None,
) -> HandwritingInference:
    """Get or create a cached inference engine.

    Reuses the same model instance for repeated calls.
    """
    key = str(checkpoint_path or "default")

    if key not in _inference_cache:
        if checkpoint_path is None:
            # Look for best checkpoint
            ckpt_dir = Path(__file__).parent / "checkpoints"
            best = ckpt_dir / "best.pt"
            final = ckpt_dir / "final.pt"
            if best.exists():
                checkpoint_path = best
            elif final.exists():
                checkpoint_path = final

        _inference_cache[key] = HandwritingInference(checkpoint_path=checkpoint_path)

    return _inference_cache[key]
