"""Graves Handwriting Synthesis Network.

Implements a 3-layer LSTM with:
  - Soft window attention over input character sequence
  - Mixture Density Network (MDN) output head
  - Generates pen strokes (Δx, Δy, pen_up) conditioned on text

Reference: Alex Graves, "Generating Sequences With Recurrent Neural Networks" (2013)
"""

from __future__ import annotations

import math
from typing import NamedTuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from .utils import VOCAB_SIZE

# ─── Config ────────────────────────────────────────────
DEFAULT_HIDDEN = 400
DEFAULT_NUM_LAYERS = 3
DEFAULT_NUM_MIXTURES = 20
DEFAULT_NUM_ATTN_MIXTURES = 10


# ─── MDN Output Container ─────────────────────────────
class MDNParams(NamedTuple):
    """Parameters of the Mixture Density Network output."""
    pi: torch.Tensor       # Mixture weights (batch, num_mixtures)
    mu_x: torch.Tensor     # Mean x (batch, num_mixtures)
    mu_y: torch.Tensor     # Mean y (batch, num_mixtures)
    sigma_x: torch.Tensor  # Std x (batch, num_mixtures)
    sigma_y: torch.Tensor  # Std y (batch, num_mixtures)
    rho: torch.Tensor      # Correlation (batch, num_mixtures)
    eos: torch.Tensor      # End-of-stroke probability (batch, 1)


# ─── Window (Attention) Layer ──────────────────────────
class WindowLayer(nn.Module):
    """Soft attention window over the character sequence.

    Uses K Gaussian attention heads to compute a soft window
    over the one-hot encoded text. The window parameters (alpha, beta, kappa)
    are predicted by the first LSTM layer.
    """

    def __init__(self, input_size: int, num_attn_mixtures: int = DEFAULT_NUM_ATTN_MIXTURES):
        super().__init__()
        self.num_attn_mixtures = num_attn_mixtures
        # Predicts 3 * K parameters: alpha (intensity), beta (width), kappa (position)
        self.linear = nn.Linear(input_size, 3 * num_attn_mixtures)

    def forward(
        self,
        lstm_out: torch.Tensor,
        text_onehot: torch.Tensor,
        prev_kappa: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Compute attention window.

        Args:
            lstm_out: Output from first LSTM, shape (batch, hidden).
            text_onehot: One-hot text, shape (batch, text_len, vocab_size).
            prev_kappa: Previous kappa, shape (batch, num_attn_mixtures).

        Returns:
            (window, new_kappa, phi) where:
              window: shape (batch, vocab_size)
              new_kappa: shape (batch, num_attn_mixtures)
              phi: attention weights, shape (batch, text_len)
        """
        params = self.linear(lstm_out)
        K = self.num_attn_mixtures

        # Split and apply activations
        alpha = torch.exp(params[:, :K])           # Intensity > 0
        beta = torch.exp(params[:, K : 2 * K])     # Width > 0
        kappa = prev_kappa + torch.exp(params[:, 2 * K :])  # Monotonic position

        # Compute phi(t, u) = sum_k alpha_k * exp(-beta_k * (kappa_k - u)^2)
        text_len = text_onehot.size(1)
        u = torch.arange(text_len, device=lstm_out.device, dtype=torch.float32)
        u = u.unsqueeze(0).unsqueeze(0)  # (1, 1, text_len)

        kappa_expanded = kappa.unsqueeze(2)   # (batch, K, 1)
        alpha_expanded = alpha.unsqueeze(2)   # (batch, K, 1)
        beta_expanded = beta.unsqueeze(2)     # (batch, K, 1)

        phi = alpha_expanded * torch.exp(-beta_expanded * (kappa_expanded - u) ** 2)
        phi = phi.sum(dim=1)  # (batch, text_len)

        # Window = phi @ text_onehot
        window = torch.bmm(phi.unsqueeze(1), text_onehot).squeeze(1)  # (batch, vocab_size)

        return window, kappa, phi


# ─── MDN Output Layer ─────────────────────────────────
class MDNLayer(nn.Module):
    """Mixture Density Network head.

    Outputs parameters for a mixture of bivariate Gaussians
    plus an end-of-stroke probability.
    """

    def __init__(self, input_size: int, num_mixtures: int = DEFAULT_NUM_MIXTURES):
        super().__init__()
        self.num_mixtures = num_mixtures
        # For each mixture: pi, mu_x, mu_y, sigma_x, sigma_y, rho = 6 params
        # Plus 1 for end-of-stroke
        self.linear = nn.Linear(input_size, num_mixtures * 6 + 1)

    def forward(self, x: torch.Tensor) -> MDNParams:
        """Compute MDN parameters from LSTM output.

        Args:
            x: Combined LSTM output, shape (batch, input_size).

        Returns:
            MDNParams with all mixture parameters.
        """
        M = self.num_mixtures
        params = self.linear(x)

        # Split parameters
        pi = params[:, :M]
        mu_x = params[:, M : 2 * M]
        mu_y = params[:, 2 * M : 3 * M]
        sigma_x = params[:, 3 * M : 4 * M]
        sigma_y = params[:, 4 * M : 5 * M]
        rho = params[:, 5 * M : 6 * M]
        eos = params[:, 6 * M :]

        # Apply activations
        pi = F.softmax(pi, dim=-1)          # Sum to 1
        sigma_x = torch.exp(sigma_x)        # > 0
        sigma_y = torch.exp(sigma_y)        # > 0
        rho = torch.tanh(rho)               # (-1, 1)
        eos = torch.sigmoid(eos)            # (0, 1)

        return MDNParams(pi, mu_x, mu_y, sigma_x, sigma_y, rho, eos)


# ─── Full Handwriting Model ───────────────────────────
class HandwritingModel(nn.Module):
    """Graves Handwriting Synthesis Network.

    Architecture:
        Input (3: dx, dy, pen_up) + Window (vocab_size)
            ↓
        LSTM Layer 1 → Window Layer (attention)
            ↓
        LSTM Layer 2 (receives: input + window + LSTM1)
            ↓
        LSTM Layer 3 (receives: input + window + LSTM2)
            ↓
        MDN Output (mixture params + eos)
    """

    def __init__(
        self,
        hidden_size: int = DEFAULT_HIDDEN,
        num_layers: int = DEFAULT_NUM_LAYERS,
        num_mixtures: int = DEFAULT_NUM_MIXTURES,
        num_attn_mixtures: int = DEFAULT_NUM_ATTN_MIXTURES,
        vocab_size: int = VOCAB_SIZE,
        input_size: int = 3,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_mixtures = num_mixtures
        self.num_attn_mixtures = num_attn_mixtures
        self.vocab_size = vocab_size
        self.input_size = input_size

        # LSTM layers (each sees: input + window + prev_layer_output)
        lstm_input_1 = input_size + vocab_size
        self.lstm1 = nn.LSTMCell(lstm_input_1, hidden_size)

        # Window attention (driven by LSTM1 output)
        self.window = WindowLayer(hidden_size, num_attn_mixtures)

        # LSTM 2 and 3 receive: input + window + prev LSTM output
        lstm_input_n = input_size + vocab_size + hidden_size
        self.lstm2 = nn.LSTMCell(lstm_input_n, hidden_size)
        self.lstm3 = nn.LSTMCell(lstm_input_n, hidden_size)

        # MDN output from all LSTM layers combined
        mdn_input = hidden_size * num_layers
        self.mdn = MDNLayer(mdn_input, num_mixtures)

    def get_initial_state(
        self, batch_size: int, device: torch.device
    ) -> dict[str, torch.Tensor]:
        """Create zero initial hidden states."""
        zeros = lambda: torch.zeros(batch_size, self.hidden_size, device=device)
        return {
            "h1": zeros(), "c1": zeros(),
            "h2": zeros(), "c2": zeros(),
            "h3": zeros(), "c3": zeros(),
            "kappa": torch.zeros(batch_size, self.num_attn_mixtures, device=device),
            "window": torch.zeros(batch_size, self.vocab_size, device=device),
        }

    def forward_step(
        self,
        x: torch.Tensor,
        text_onehot: torch.Tensor,
        state: dict[str, torch.Tensor],
    ) -> tuple[MDNParams, dict[str, torch.Tensor], torch.Tensor]:
        """Single timestep forward pass.

        Args:
            x: Input stroke, shape (batch, 3).
            text_onehot: One-hot text, shape (batch, text_len, vocab_size).
            state: Hidden states dict from previous step.

        Returns:
            (mdn_params, new_state, phi).
        """
        # LSTM 1
        inp1 = torch.cat([x, state["window"]], dim=1)
        h1, c1 = self.lstm1(inp1, (state["h1"], state["c1"]))

        # Attention window (driven by LSTM1)
        window, kappa, phi = self.window(h1, text_onehot, state["kappa"])

        # LSTM 2
        inp2 = torch.cat([x, window, h1], dim=1)
        h2, c2 = self.lstm2(inp2, (state["h2"], state["c2"]))

        # LSTM 3
        inp3 = torch.cat([x, window, h2], dim=1)
        h3, c3 = self.lstm3(inp3, (state["h3"], state["c3"]))

        # MDN output from all layers
        combined = torch.cat([h1, h2, h3], dim=1)
        mdn_params = self.mdn(combined)

        new_state = {
            "h1": h1, "c1": c1,
            "h2": h2, "c2": c2,
            "h3": h3, "c3": c3,
            "kappa": kappa,
            "window": window,
        }

        return mdn_params, new_state, phi

    def forward(
        self,
        strokes: torch.Tensor,
        text_onehot: torch.Tensor,
        state: dict[str, torch.Tensor] | None = None,
    ) -> tuple[list[MDNParams], dict[str, torch.Tensor], list[torch.Tensor]]:
        """Full sequence forward pass.

        Args:
            strokes: Input strokes, shape (batch, seq_len, 3).
            text_onehot: One-hot text, shape (batch, text_len, vocab_size).
            state: Optional initial state (defaults to zeros).

        Returns:
            (list_of_mdn_params, final_state, list_of_phi).
        """
        batch_size, seq_len, _ = strokes.shape

        if state is None:
            state = self.get_initial_state(batch_size, strokes.device)

        all_mdn: list[MDNParams] = []
        all_phi: list[torch.Tensor] = []

        for t in range(seq_len):
            x_t = strokes[:, t, :]
            mdn_params, state, phi = self.forward_step(x_t, text_onehot, state)
            all_mdn.append(mdn_params)
            all_phi.append(phi)

        return all_mdn, state, all_phi


# ─── Loss Function ─────────────────────────────────────
def mdn_loss(
    mdn_params: MDNParams,
    target: torch.Tensor,
) -> torch.Tensor:
    """Compute negative log-likelihood of the MDN.

    Args:
        mdn_params: MDN output parameters.
        target: Target stroke, shape (batch, 3) — (dx, dy, pen_up).

    Returns:
        Scalar loss.
    """
    dx = target[:, 0:1]     # (batch, 1)
    dy = target[:, 1:2]     # (batch, 1)
    pen = target[:, 2:3]    # (batch, 1)

    pi = mdn_params.pi
    mu_x = mdn_params.mu_x
    mu_y = mdn_params.mu_y
    sigma_x = mdn_params.sigma_x
    sigma_y = mdn_params.sigma_y
    rho = mdn_params.rho
    eos = mdn_params.eos

    # Bivariate Gaussian PDF
    z_x = (dx - mu_x) / (sigma_x + 1e-8)
    z_y = (dy - mu_y) / (sigma_y + 1e-8)
    z = z_x ** 2 + z_y ** 2 - 2 * rho * z_x * z_y

    denom = 1.0 - rho ** 2 + 1e-8
    exponent = -z / (2 * denom)
    norm = 2 * math.pi * sigma_x * sigma_y * torch.sqrt(denom + 1e-8) + 1e-8

    gaussian = torch.exp(exponent) / norm

    # Weighted mixture
    gmm = torch.sum(pi * gaussian, dim=1, keepdim=True)
    gmm = torch.clamp(gmm, min=1e-20)

    # Stroke loss (NLL of mixture)
    stroke_loss = -torch.log(gmm)

    # End-of-stroke loss (binary cross-entropy)
    eos_loss = -pen * torch.log(eos + 1e-8) - (1 - pen) * torch.log(1 - eos + 1e-8)

    return (stroke_loss + eos_loss).mean()
