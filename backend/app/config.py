"""Application settings loaded from environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the HandwritOCR backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ─── Server ─────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # ─── Redis ──────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ─── Storage ────────────────────────────────────
    storage_path: str = "./storage"

    # ─── Upload Limits ──────────────────────────────
    max_upload_size_mb: int = 10
    max_samples_per_session: int = 20

    # ─── CORS ───────────────────────────────────────
    cors_origins: str = "http://localhost:3000"

    # ─── Celery ─────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins."""
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def storage_dir(self) -> Path:
        """Resolved storage directory path."""
        p = Path(self.storage_path)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def upload_dir(self) -> Path:
        """Directory for uploaded samples."""
        p = self.storage_dir / "uploads"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def output_dir(self) -> Path:
        """Directory for generated outputs."""
        p = self.storage_dir / "outputs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
