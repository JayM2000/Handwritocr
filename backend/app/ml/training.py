"""Training pipeline for the handwriting synthesis model.

Provides:
  - HandwritingTrainer class with training loop, validation, checkpointing
  - CLI entry point for running training
  - MDN loss computation over sequences
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim

from .model import HandwritingModel, mdn_loss
from .dataset import IAMDataset, SyntheticStrokeDataset, create_dataloader

logger = logging.getLogger(__name__)

# ─── Default Hyperparameters ──────────────────────────
DEFAULTS = {
    "hidden_size": 400,
    "num_layers": 3,
    "num_mixtures": 20,
    "num_attn_mixtures": 10,
    "learning_rate": 1e-3,
    "batch_size": 32,
    "epochs": 100,
    "grad_clip": 10.0,
    "lr_decay": 0.995,
    "min_lr": 1e-6,
    "val_split": 0.1,
    "checkpoint_every": 5,
    "patience": 15,
}


# ─── Trainer ──────────────────────────────────────────
class HandwritingTrainer:
    """Training manager for the handwriting synthesis model."""

    def __init__(
        self,
        model: HandwritingModel,
        checkpoint_dir: str | Path = "app/ml/checkpoints",
        device: str | None = None,
        **kwargs,
    ):
        self.model = model
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.device = torch.device(
            device or ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.model.to(self.device)

        # Hyperparameters (merge defaults with kwargs)
        self.hp = {**DEFAULTS, **kwargs}

        self.optimizer = optim.Adam(
            model.parameters(), lr=self.hp["learning_rate"]
        )
        self.scheduler = optim.lr_scheduler.ExponentialLR(
            self.optimizer, gamma=self.hp["lr_decay"]
        )

        self.epoch = 0
        self.best_val_loss = float("inf")
        self.patience_counter = 0

        logger.info(f"Trainer initialized on {self.device}")
        logger.info(f"Model params: {sum(p.numel() for p in model.parameters()):,}")

    def train(
        self,
        train_dataset,
        val_dataset=None,
    ) -> dict:
        """Run the full training loop.

        Args:
            train_dataset: Training dataset.
            val_dataset: Optional validation dataset.

        Returns:
            Dict with training history.
        """
        train_loader = create_dataloader(
            train_dataset,
            batch_size=self.hp["batch_size"],
            shuffle=True,
        )

        val_loader = None
        if val_dataset:
            val_loader = create_dataloader(
                val_dataset,
                batch_size=self.hp["batch_size"],
                shuffle=False,
            )

        history = {"train_loss": [], "val_loss": [], "lr": []}

        for epoch in range(self.hp["epochs"]):
            self.epoch = epoch + 1
            t0 = time.time()

            # Train
            train_loss = self._train_epoch(train_loader)
            history["train_loss"].append(train_loss)

            # Validate
            val_loss = None
            if val_loader:
                val_loss = self._validate(val_loader)
                history["val_loss"].append(val_loss)

            # Learning rate
            current_lr = self.optimizer.param_groups[0]["lr"]
            history["lr"].append(current_lr)
            if current_lr > self.hp["min_lr"]:
                self.scheduler.step()

            elapsed = time.time() - t0

            # Logging
            msg = f"Epoch {self.epoch}/{self.hp['epochs']} | loss={train_loss:.4f}"
            if val_loss is not None:
                msg += f" | val_loss={val_loss:.4f}"
            msg += f" | lr={current_lr:.2e} | {elapsed:.1f}s"
            logger.info(msg)

            # Checkpoint
            if self.epoch % self.hp["checkpoint_every"] == 0:
                self.save_checkpoint(f"epoch_{self.epoch}.pt")

            # Early stopping
            check_loss = val_loss if val_loss is not None else train_loss
            if check_loss < self.best_val_loss:
                self.best_val_loss = check_loss
                self.patience_counter = 0
                self.save_checkpoint("best.pt")
            else:
                self.patience_counter += 1
                if self.patience_counter >= self.hp["patience"]:
                    logger.info(f"Early stopping at epoch {self.epoch}")
                    break

        # Save final
        self.save_checkpoint("final.pt")
        return history

    def _train_epoch(self, loader) -> float:
        """Run one training epoch."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        for batch in loader:
            strokes = batch["strokes"].to(self.device)
            text_onehot = batch["text_onehot"].to(self.device)

            # Input: strokes[:-1], Target: strokes[1:]
            input_strokes = strokes[:, :-1, :]
            target_strokes = strokes[:, 1:, :]

            # Forward pass
            self.optimizer.zero_grad()
            mdn_params_list, _, _ = self.model(input_strokes, text_onehot)

            # Compute loss over sequence
            loss = torch.tensor(0.0, device=self.device)
            seq_len = target_strokes.size(1)

            for t in range(min(seq_len, len(mdn_params_list))):
                loss += mdn_loss(mdn_params_list[t], target_strokes[:, t, :])

            loss = loss / seq_len

            # Backward
            loss.backward()
            nn.utils.clip_grad_norm_(self.model.parameters(), self.hp["grad_clip"])
            self.optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        return total_loss / max(num_batches, 1)

    @torch.no_grad()
    def _validate(self, loader) -> float:
        """Run validation."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        for batch in loader:
            strokes = batch["strokes"].to(self.device)
            text_onehot = batch["text_onehot"].to(self.device)

            input_strokes = strokes[:, :-1, :]
            target_strokes = strokes[:, 1:, :]

            mdn_params_list, _, _ = self.model(input_strokes, text_onehot)

            loss = torch.tensor(0.0, device=self.device)
            seq_len = target_strokes.size(1)

            for t in range(min(seq_len, len(mdn_params_list))):
                loss += mdn_loss(mdn_params_list[t], target_strokes[:, t, :])

            total_loss += (loss / seq_len).item()
            num_batches += 1

        return total_loss / max(num_batches, 1)

    def save_checkpoint(self, filename: str) -> Path:
        """Save model checkpoint."""
        path = self.checkpoint_dir / filename
        torch.save({
            "epoch": self.epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "best_val_loss": self.best_val_loss,
            "hp": self.hp,
        }, path)
        logger.info(f"Checkpoint saved: {path}")
        return path

    def load_checkpoint(self, path: str | Path) -> None:
        """Load model checkpoint."""
        ckpt = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(ckpt["model_state_dict"])
        self.optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        self.epoch = ckpt.get("epoch", 0)
        self.best_val_loss = ckpt.get("best_val_loss", float("inf"))
        logger.info(f"Checkpoint loaded: {path} (epoch {self.epoch})")


# ─── CLI Entry Point ──────────────────────────────────
def train_cli(
    data_dir: str | None = None,
    checkpoint_dir: str = "app/ml/checkpoints",
    epochs: int = 100,
    batch_size: int = 32,
    use_synthetic: bool = False,
    device: str | None = None,
) -> None:
    """CLI-callable training function.

    Args:
        data_dir: Path to IAM dataset directory.
        checkpoint_dir: Where to save checkpoints.
        epochs: Number of training epochs.
        batch_size: Batch size.
        use_synthetic: If True, use synthetic data (for testing).
        device: 'cuda' or 'cpu'.
    """
    logging.basicConfig(level=logging.INFO)

    # Create model
    model = HandwritingModel()

    # Create dataset
    if use_synthetic or data_dir is None:
        logger.info("Using synthetic dataset for training")
        train_dataset = SyntheticStrokeDataset(num_samples=1000)
        val_dataset = SyntheticStrokeDataset(num_samples=100)
    else:
        full_dataset = IAMDataset(data_dir)
        # Split train/val
        total = len(full_dataset)
        val_size = int(total * 0.1)
        train_size = total - val_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            full_dataset, [train_size, val_size]
        )

    # Train
    trainer = HandwritingTrainer(
        model,
        checkpoint_dir=checkpoint_dir,
        device=device,
        epochs=epochs,
        batch_size=batch_size,
    )

    trainer.train(train_dataset, val_dataset)
    logger.info("Training complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train handwriting synthesis model")
    parser.add_argument("--data-dir", type=str, default=None, help="IAM dataset path")
    parser.add_argument("--checkpoint-dir", type=str, default="app/ml/checkpoints")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--synthetic", action="store_true", help="Use synthetic data")
    parser.add_argument("--device", type=str, default=None)
    args = parser.parse_args()

    train_cli(
        data_dir=args.data_dir,
        checkpoint_dir=args.checkpoint_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        use_synthetic=args.synthetic,
        device=args.device,
    )
