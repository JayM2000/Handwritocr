"""Tests for the health endpoint."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Root endpoint returns app info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "HandwritOCR API"
    assert "version" in data


def test_health():
    """Health endpoint returns ok status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "redis" in data
    assert "celery" in data


def test_upload_no_files():
    """Upload with no files returns 400."""
    response = client.post("/api/samples/upload")
    assert response.status_code in (400, 422)


def test_generate_invalid_session():
    """Generate with invalid session returns 404."""
    response = client.post(
        "/api/generate",
        json={
            "session_id": "nonexistent",
            "text": "Hello world",
        },
    )
    assert response.status_code == 404


def test_download_nonexistent():
    """Download nonexistent task returns 404."""
    response = client.get("/api/download/nonexistent")
    assert response.status_code == 404
